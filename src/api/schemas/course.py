from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.course import CreateCourseForm
from api.utils.points import POINTS_COURSE_MULTIPLIER, get_points_for_target
from api.utils.vote import AbstractDownvoteMutation, AbstractUpvoteMutation
from app.models import Course


class CourseObjectType(DjangoObjectType):
    points = graphene.Int()
    resource_count = graphene.Int()

    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "code",
            "subject",
            "school",
            "creator",
            "modified",
            "created",
            "resources",
        )

    def resolve_points(self, info: ResolveInfo) -> int:
        return get_points_for_target(self, POINTS_COURSE_MULTIPLIER)

    def resolve_resource_count(self, info: ResolveInfo) -> int:
        return self.resources.count()


class CreateCourseMutation(DjangoModelFormMutation):
    course = graphene.Field(CourseObjectType)

    class Meta:
        form_class = CreateCourseForm

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: CreateCourseForm, info: ResolveInfo
    ) -> "CreateCourseMutation":
        course = Course.objects.create(creator=info.context.user, **form.cleaned_data)
        return cls(course=course)


class UpvoteCourseMutation(AbstractUpvoteMutation):
    class Arguments:
        course_id = graphene.Int()

    course = graphene.Field(CourseObjectType)


class DownvoteCourseMutation(AbstractDownvoteMutation):
    class Arguments:
        course_id = graphene.Int()

    course = graphene.Field(CourseObjectType)


class Query(graphene.ObjectType):
    courses = graphene.List(
        CourseObjectType,
        course_name=graphene.String(),
        course_code=graphene.String(),
        subject_id=graphene.Int(),
        school_id=graphene.Int(),
        school_type_id=graphene.Int(),
        country_id=graphene.Int(),
        city_id=graphene.Int(),
    )

    course = graphene.Field(CourseObjectType, course_id=graphene.Int())

    def resolve_courses(
        self,
        info: ResolveInfo,
        course_name: Optional[str] = None,
        course_code: Optional[str] = None,
        subject_id: Optional[int] = None,
        school_id: Optional[int] = None,
        school_type_id: Optional[int] = None,
        country_id: Optional[int] = None,
        city_id: Optional[int] = None,
    ) -> List[Course]:
        """Filter courses based on the query parameters."""

        courses = Course.objects.all()

        if course_name is not None:
            courses = courses.filter(name__icontains=course_name)
        if course_code is not None:
            courses = courses.filter(code__icontains=course_code)
        if subject_id is not None:
            courses = courses.filter(subject__pk=subject_id)
        if school_id is not None:
            courses = courses.filter(school__pk=school_id)
        if school_type_id is not None:
            courses = courses.filter(school__school_type__pk=school_type_id)
        if country_id is not None:
            courses = courses.filter(school__city__country__pk=country_id)
        if city_id is not None:
            courses = courses.filter(school__city__pk=city_id)

        return courses

    def resolve_course(
        self, info: ResolveInfo, course_id: Optional[int] = None
    ) -> Optional[Course]:
        try:
            return Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            # Return None instead of throwing a GraphQL Error.
            return None


class Mutation(graphene.ObjectType):
    create_course = CreateCourseMutation.Field()
    upvote_course = UpvoteCourseMutation.Field()
    downvote_course = DownvoteCourseMutation.Field()
