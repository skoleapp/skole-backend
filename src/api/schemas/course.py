from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_extensions.auth.decorators import login_required

from api.forms.course import CreateCourseForm
from api.schemas.resource import ResourceType
from api.schemas.user import UserTypePublic
from api.utils.points import get_points_for_course
from app.models import Course, Resource


class CourseType(DjangoObjectType):
    creator = graphene.Field(UserTypePublic)
    resources = graphene.List(ResourceType)
    points = graphene.Int()

    class Meta:
        model = Course
        fields = ("id", "name", "code", "subject", "school", "creator", "points", "modified", "created", "resources")

    def resolve_resources(self, info: ResolveInfo) -> List[Resource]:
        return self.resources.all()

    def resolve_points(self, info: ResolveInfo) -> int:
        return get_points_for_course(self)


class CreateCourseMutation(DjangoModelFormMutation):
    course = graphene.Field(CourseType)

    class Meta:
        form_class = CreateCourseForm

    @classmethod
    @login_required
    def perform_mutate(cls, form: CreateCourseForm, info: ResolveInfo) -> 'CreateCourseMutation':
        course = Course.objects.create(creator=info.context.user, **form.cleaned_data)
        return cls(course=course)


class Query(graphene.ObjectType):
    courses = graphene.List(
        CourseType,
        course_name=graphene.String(),
        course_code=graphene.String(),
        subject_id=graphene.Int(),
        school_id=graphene.Int()
    )

    course = graphene.Field(CourseType, course_id=graphene.Int())

    def resolve_courses(
            self,
            info: ResolveInfo,
            course_name: Optional[str] = None,
            course_code: Optional[str] = None,
            subject_id: Optional[int] = None,
            school_id: Optional[int] = None
    ) -> List[Course]:
        courses = Course.objects.all()

        if course_name is not None:
            courses = courses.filter(name__icontains=course_name)
        if course_code is not None:
            courses = courses.filter(code__icontains=course_code)
        if subject_id is not None:
            courses = courses.filter(subject__pk=subject_id)
        if school_id is not None:
            courses = courses.filter(school__pk=school_id)

        return courses

    def resolve_course(self, info: ResolveInfo, course_id: int) -> Course:
        return Course.objects.get(pk=course_id)


class Mutation(graphene.ObjectType):
    create_course = CreateCourseMutation.Field()
