from typing import Optional, cast, get_args

import graphene
from django.conf import settings
from django.db.models import F, Q, QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import GraphQLError

from skole.forms import CreateCourseForm, DeleteCourseForm
from skole.models import Course, User
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
from skole.types import CourseOrderingOption, ResolveInfo
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
    slug = graphene.String()
    star_count = graphene.Int()
    resource_count = graphene.Int()
    comment_count = graphene.Int()

    class Meta:
        model = Course
        fields = (
            "id",
            "slug",
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
        search_term=graphene.String(),
        subject=graphene.String(),
        school=graphene.String(),
        school_type=graphene.String(),
        country=graphene.String(),
        city=graphene.String(),
        user=graphene.String(),
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
    )

    autocomplete_courses = graphene.List(
        CourseObjectType,
        school=graphene.String(),
        name=graphene.String(),
    )

    starred_courses = graphene.Field(
        PaginatedCourseObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
    )

    course = graphene.Field(CourseObjectType, slug=graphene.String())

    @staticmethod
    def resolve_courses(
        root: None,
        info: ResolveInfo,
        search_term: Optional[str] = None,
        subject: str = "",
        school: str = "",
        school_type: str = "",
        country: str = "",
        city: str = "",
        user: str = "",
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
        ordering: CourseOrderingOption = "best",
    ) -> PaginatedCourseObjectType:
        """
        Return courses filtered by query params.

        The `search_term` can be either the course name or the course code.

        Results are sorted either manually based on query params or by secret Skole AI-
        powered algorithms.
        """

        qs: QuerySet[Course] = Course.objects.all()

        if search_term is not None:
            qs = qs.filter(
                Q(name__icontains=search_term) | Q(code__icontains=search_term)
            )

        if subject != "":
            qs = qs.filter(subjects__slug=subject)
        if school != "":
            qs = qs.filter(school__slug=school)
        if school_type != "":
            qs = qs.filter(school__school_type__slug=school_type)
        if country != "":
            qs = qs.filter(school__city__country__slug=country)
        if city != "":
            qs = qs.filter(school__city__slug=city)
        if user != "":
            qs = qs.filter(user__slug=user)

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
        root: None, info: ResolveInfo, school: str = "", name: str = ""
    ) -> QuerySet[Course]:
        """Results are sorted by secret Skole AI-powered algorithms."""
        qs: QuerySet[Course] = Course.objects.order_by("name")

        if school != "":
            qs = qs.filter(school__slug=school)

        if name != "":
            qs = qs.filter(Q(name__icontains=name) | Q(code__icontains=name))

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
        user = cast(User, info.context.user)
        qs = Course.objects.filter(stars__user=user)
        qs = qs.order_by("pk")
        return get_paginator(qs, page_size, page, PaginatedCourseObjectType)

    @staticmethod
    def resolve_course(
        root: None, info: ResolveInfo, slug: str = ""
    ) -> Optional[Course]:
        return Course.objects.get_or_none(slug=slug)


class Mutation(SkoleObjectType):
    create_course = CreateCourseMutation.Field()
    delete_course = DeleteCourseMutation.Field()
