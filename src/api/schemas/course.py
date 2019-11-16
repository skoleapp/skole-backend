from typing import List

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_extensions.auth.decorators import login_required

from api.schemas.user import UserTypePublic
from api.types.resource import ResourceType
from app.models import Course
from api.forms import CreateCourseForm


class CourseType(DjangoObjectType):
    creator = graphene.Field(UserTypePublic)
    resources = graphene.List(ResourceType)

    class Meta:
        model = Course
        fields = ("id", "name", "code", "subject", "school", "creator", "points", "modified", "created", "resources")


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
    courses = graphene.List(CourseType, subject_id=graphene.Int(), school_id=graphene.Int())
    course = graphene.Field(CourseType, id=graphene.Int())

    def resolve_courses(self, info: ResolveInfo, subject_id: int = None, school_id: int = None) -> List[Course]:
        courses = Course.objects.all()

        if subject_id is not None:
            courses = courses.filter(subject__pk=subject_id)
        if school_id is not None:
            courses = courses.filter(school__pk=school_id)

        return courses

    def resolve_course(self, info: ResolveInfo, id: int) -> Course:
        return Course.objects.get(pk=id)


class Mutation(graphene.ObjectType):
    create_course = CreateCourseMutation.Field()
