from typing import Optional, get_args

import graphene
from django.conf import settings
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import GraphQLError

from skole.forms import CreateCourseForm, DeleteCourseForm
from skole.models import Course
from skole.overridden import login_required
from skole.schemas.base import (
    SkoleCreateUpdateMutationMixin,
    SkoleDeleteMutationMixin,
    SkoleObjectType,
)
from skole.schemas.mixins import (
    PaginationMixin,
    StarMixin,
    SuccessMessageMixin,
    VoteMixin,
)
from skole.types import ID, CourseOrderingOption, ResolveInfo
from skole.utils.constants import GraphQLErrors, Messages
from skole.utils.pagination import get_paginator


def order_courses_with_secret_algorithm(qs: QuerySet[Course]) -> QuerySet[Course]:
    """
    Sort the given queryset so that the most interesting courses come first.

    No deep logic in this, should just be a formula that makes the most sense for
    determining the most interesting courses.

    The ordering formula/value should not be exposed to the frontend.
    """

    return qs.order_by(
        -(3 * F("score") + 2 * F("resource_count") + F("comment_count")), "name"
    )


class CourseObjectType(VoteMixin, StarMixin, DjangoObjectType):
    star_count = graphene.Int()
    resource_count = graphene.Int()
    comment_count = graphene.Int()

    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "code",
            "subjects",
            "school",
            "user",
            "resources",
            "comments",
            "score",
            "star_count",
            "resource_count",
            "comment_count",
            "modified",
            "created",
        )

    # Have to specify these with resolvers since graphene
    # cannot infer the annotated fields otherwise.

    @staticmethod
    def resolve_star_count(root: Course, info: ResolveInfo) -> int:
        return getattr(root, "star_count", 0)

    @staticmethod
    def resolve_comment_count(root: Course, info: ResolveInfo) -> int:
        # When the Course is created and returned from a ModelForm it will not have
        # this field computed (it gets annotated only in the model manager) since the
        # value of this would be obviously 0 at the time of the course's creation,
        # it's ok to return it as the default here.
        return getattr(root, "comment_count", 0)

    @staticmethod
    def resolve_resource_count(root: Course, info: ResolveInfo) -> int:
        return getattr(root, "resource_count", 0)


class PaginatedCourseObjectType(PaginationMixin, SkoleObjectType):
    objects = graphene.List(CourseObjectType)

    class Meta:
        description = Course.__doc__


class CreateCourseMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """Create a new course."""

    verification_required = True
    success_message_value = Messages.COURSE_CREATED
    course = graphene.Field(CourseObjectType)

    class Meta:
        form_class = CreateCourseForm
        exclude_fields = ("id",)


class DeleteCourseMutation(SkoleDeleteMutationMixin, DjangoModelFormMutation):
    """Delete a course."""

    success_message_value = Messages.COURSE_DELETED

    class Meta(SkoleDeleteMutationMixin.Meta):
        form_class = DeleteCourseForm


class Query(SkoleObjectType):
    courses = graphene.Field(
        PaginatedCourseObjectType,
        course_name=graphene.String(),
        course_code=graphene.String(),
        subject=graphene.ID(),
        school=graphene.ID(),
        school_type=graphene.ID(),
        country=graphene.ID(),
        city=graphene.ID(),
        user=graphene.ID(),
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
    )

    autocomplete_courses = graphene.List(
        CourseObjectType,
        school=graphene.ID(),
        name=graphene.String(),
    )

    starred_courses = graphene.Field(
        PaginatedCourseObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
    )

    course = graphene.Field(CourseObjectType, id=graphene.ID())

    @staticmethod
    def resolve_courses(
        root: None,
        info: ResolveInfo,
        course_name: Optional[str] = None,
        course_code: Optional[str] = None,
        subject: ID = None,
        school: ID = None,
        school_type: ID = None,
        country: ID = None,
        city: ID = None,
        user: ID = None,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
        ordering: CourseOrderingOption = "best",
    ) -> PaginatedCourseObjectType:
        """
        Return courses filtered by query params.

        Results are sorted either manually based on query params or by secret Skole AI-
        powered algorithms.
        """

        qs: QuerySet[Course] = Course.objects.all()

        if course_name is not None:
            qs = qs.filter(name__icontains=course_name)
        if course_code is not None:
            qs = qs.filter(code__icontains=course_code)
        if subject is not None:
            qs = qs.filter(subjects__pk=subject)
        if school is not None:
            qs = qs.filter(school__pk=school)
        if school_type is not None:
            qs = qs.filter(school__school_type__pk=school_type)
        if country is not None:
            qs = qs.filter(school__city__country__pk=country)
        if city is not None:
            qs = qs.filter(school__city__pk=city)
        if user is not None:
            qs = qs.filter(user__pk=user)

        if ordering not in get_args(CourseOrderingOption):
            raise GraphQLError(GraphQLErrors.INVALID_ORDERING)

        if ordering == "best":
            qs = order_courses_with_secret_algorithm(qs)
        elif ordering == "score":
            qs = qs.order_by("-score", "name")
        else:  # name or -name
            qs = qs.order_by(ordering)

        return get_paginator(qs, page_size, page, PaginatedCourseObjectType)

    @staticmethod
    def resolve_autocomplete_courses(
        root: None, info: ResolveInfo, school: ID = None, name: str = ""
    ) -> QuerySet[Course]:
        """Results are sorted by secret Skole AI-powered algorithms."""
        qs: QuerySet[Course] = Course.objects.order_by("name")

        if school is not None:
            qs = qs.filter(school__pk=school)

        if name != "":
            qs = qs.filter(name__icontains=name)

        qs = order_courses_with_secret_algorithm(qs)
        return qs[: settings.AUTOCOMPLETE_MAX_RESULTS]

    @staticmethod
    @login_required
    def resolve_starred_courses(
        root: None,
        info: ResolveInfo,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> PaginatedCourseObjectType:
        """
        Return starred courses of the user making the query.

        Results are sorted by creation time. Return an empty list for unauthenticated
        users.
        """
        qs = Course.objects.filter(stars__user__pk=info.context.user.pk)
        qs = qs.order_by("pk")
        return get_paginator(qs, page_size, page, PaginatedCourseObjectType)

    @staticmethod
    def resolve_course(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[Course]:
        return Course.objects.get_or_none(pk=id)


class Mutation(SkoleObjectType):
    create_course = CreateCourseMutation.Field()
    delete_course = DeleteCourseMutation.Field()
