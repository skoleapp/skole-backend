from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.course import CreateCourseForm
from api.schemas.vote import VoteObjectType
from api.utils.common import get_obj_or_none
from api.utils.points import get_points_for_target
from core.models import Course, Vote


class CourseObjectType(DjangoObjectType):
    points = graphene.Int()
    resource_count = graphene.Int()
    vote = graphene.Field(VoteObjectType)

    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "code",
            "subject",
            "school",
            "user",
            "modified",
            "created",
            "resources",
            "comments",
        )

    def resolve_points(self, info: ResolveInfo) -> int:
        return get_points_for_target(self)

    def resolve_vote(self, info: ResolveInfo) -> Optional[int]:
        """Resolve current user's vote if it exists."""

        user = info.context.user

        if user.is_anonymous:
            return None

        try:
            return user.votes.get(comment=self.pk)
        except Vote.DoesNotExist:
            return None


class CreateCourseMutation(DjangoModelFormMutation):
    course = graphene.Field(CourseObjectType)

    class Meta:
        form_class = CreateCourseForm
        exclude_fields = ("id",)

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: CreateCourseForm, info: ResolveInfo
    ) -> "CreateCourseMutation":
        course = Course.objects.create(user=info.context.user, **form.cleaned_data)
        return cls(course=course)


class Query(graphene.ObjectType):
    courses = graphene.List(
        CourseObjectType,
        course_name=graphene.String(),
        course_code=graphene.String(),
        subject=graphene.ID(),
        school=graphene.ID(),
        school_type=graphene.ID(),
        country=graphene.ID(),
        city=graphene.ID(),
    )

    course = graphene.Field(CourseObjectType, id=graphene.ID())

    @login_required
    def resolve_courses(
        self,
        info: ResolveInfo,
        course_name: Optional[str] = None,
        course_code: Optional[str] = None,
        subject: Optional[int] = None,
        school: Optional[int] = None,
        school_type: Optional[int] = None,
        country: Optional[int] = None,
        city: Optional[int] = None,
    ) -> "QuerySet[Course]":
        """Filter courses based on the query parameters."""

        courses = Course.objects.order_by("name")

        if course_name is not None:
            courses = courses.filter(name__icontains=course_name)
        if course_code is not None:
            courses = courses.filter(code__icontains=course_code)
        if subject is not None:
            courses = courses.filter(subject__pk=subject)
        if school is not None:
            courses = courses.filter(school__pk=school)
        if school_type is not None:
            courses = courses.filter(school__school_type__pk=school_type)
        if country is not None:
            courses = courses.filter(school__city__country__pk=country)
        if city is not None:
            courses = courses.filter(school__city__pk=city)

        return courses

    @login_required
    def resolve_course(
        self, info: ResolveInfo, id: Optional[int] = None
    ) -> Optional[Course]:
        return get_obj_or_none(Course, id)


class Mutation(graphene.ObjectType):
    create_course = CreateCourseMutation.Field()
