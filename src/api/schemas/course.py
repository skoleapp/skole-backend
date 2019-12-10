from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_extensions.auth.decorators import login_required

from api.forms.course import CreateCourseForm
from api.utils.points import get_points_for_course
from app.models import Course, Vote
from app.utils.vote import UPVOTE


class CourseType(DjangoObjectType):
    points = graphene.Int()
    resource_count = graphene.Int()

    class Meta:
        model = Course
        fields = ("id", "name", "code", "subject", "school", "creator", "modified", "created", "resources")

    def resolve_points(self, info: ResolveInfo) -> int:
        return get_points_for_course(self)

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


class UpvoteCourseMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.Int()
    course = graphene.Field(CourseType)

    @login_required
    def mutate(self, info: ResolveInfo, course_id: int) -> 'UpvoteCourseMutation':
        course = Course.objects.get(pk=course_id)
        try:
            vote = course.votes.get(pk=info.context.user.id)
            if vote.status == UPVOTE:
                return UpvoteCourseMutation(course=course)
            else:
                vote.delete()
        except Vote.DoesNotExist:
            pass

        Vote.objects.create_vote(
            creator=info.context.user,
            status=UPVOTE,
            target=course,
        )
        return UpvoteCourseMutation(course=course)


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
    upvote_course = UpvoteCourseMutation.Field()
