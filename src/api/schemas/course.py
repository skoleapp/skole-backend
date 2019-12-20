from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.course import CreateCourseForm
from api.utils.points import get_points_for_target, POINTS_COURSE_MULTIPLIER
from api.utils.vote import AbstractDownvoteMutation, AbstractUpvoteMutation
from app.models import Course


class CourseType(DjangoObjectType):
    points = graphene.Int()
    resource_count = graphene.Int()

    class Meta:
        model = Course
        fields = ("id", "name", "code", "subject", "school", "creator", "modified", "created", "resources")

    def resolve_points(self, info: ResolveInfo) -> int:
        return get_points_for_target(self, POINTS_COURSE_MULTIPLIER)

    def resolve_resource_count(self, info: ResolveInfo) -> int:
        return self.resources.count()


class CreateCourseMutation(DjangoModelFormMutation):
    course = graphene.Field(CourseType)

    class Meta:
        form_class = CreateCourseForm

    @classmethod
    @login_required
    def perform_mutate(cls, form: CreateCourseForm, info: ResolveInfo) -> 'CreateCourseMutation':
        course = Course.objects.create(creator=info.context.user, **form.cleaned_data)
        return cls(course=course)


class UpvoteCourseMutation(AbstractUpvoteMutation):
    class Input:
        course_id = graphene.Int()

    course = graphene.Field(CourseType)


class DownvoteCourseMutation(AbstractDownvoteMutation):
    class Input:
        course_id = graphene.Int()

    course = graphene.Field(CourseType)


class Query(graphene.ObjectType):
    courses = graphene.List(
        CourseType,
        course_name=graphene.String(),
        course_code=graphene.String(),
        subject_name=graphene.String(),
        school_name=graphene.String(),
        school_type=graphene.String(),
        country_name=graphene.String(),
        city_name=graphene.String(),
    )
    course = graphene.Field(CourseType, course_id=graphene.Int())

    def resolve_courses(self, info: ResolveInfo,
                        course_name: Optional[str] = None,
                        course_code: Optional[str] = None,
                        subject_name: Optional[str] = None,
                        school_name: Optional[str] = None,
                        school_type: Optional[int] = None,
                        country_name: Optional[str] = None,
                        city_name: Optional[str] = None) -> List[Course]:
        courses = Course.objects.all()

        if course_name is not None:
            courses = courses.filter(name__icontains=course_name)
        if course_code is not None:
            courses = courses.filter(code__icontains=course_code)
        if subject_name is not None:
            courses = courses.filter(subject__name__icontains=subject_name)
        if school_name is not None:
            courses = courses.filter(school__name__icontains=school_name)
        if school_type is not None:
            courses = courses.filter(school__school_type__name__iexact=school_type)
        if country_name is not None:
            courses = courses.filter(school__city__country__name__iexact=country_name)
        if city_name is not None:
            courses = courses.filter(school__city__name__iexact=city_name)

        return courses

    def resolve_course(self, info: ResolveInfo, course_id: int) -> Course:
        return Course.objects.get(pk=course_id)


class Mutation(graphene.ObjectType):
    create_course = CreateCourseMutation.Field()
    upvote_course = UpvoteCourseMutation.Field()
    downvote_course = DownvoteCourseMutation.Field()
