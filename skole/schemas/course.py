from typing import Optional, get_args

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import GraphQLError, ResolveInfo
from graphql_jwt.decorators import login_required

from skole.forms.course import CreateCourseForm, DeleteCourseForm
from skole.models import Course
from skole.utils.constants import GraphQLErrors, Messages
from skole.utils.mixins import (
    DeleteMutationMixin,
    LoginRequiredMutationMixin,
    MessageMixin,
    PaginationMixin,
    StarredMixin,
    VoteMixin,
)
from skole.utils.pagination import get_paginator
from skole.utils.shortcuts import get_obj_or_none
from skole.utils.types import ID, CourseOrderingOption


class CourseObjectType(VoteMixin, StarredMixin, DjangoObjectType):
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


class PaginatedCourseObjectType(PaginationMixin, graphene.ObjectType):
    objects = graphene.List(CourseObjectType)


class CreateCourseMutation(
    LoginRequiredMutationMixin, MessageMixin, DjangoModelFormMutation
):
    course = graphene.Field(CourseObjectType)

    class Meta:
        form_class = CreateCourseForm
        exclude_fields = ("id",)

    @classmethod
    def perform_mutate(
        cls, form: CreateCourseForm, info: ResolveInfo
    ) -> "CreateCourseMutation":
        assert info.context is not None
        course = Course.objects.create(user=info.context.user, **form.cleaned_data)
        return cls(course=course, message=Messages.COURSE_CREATED)


class DeleteCourseMutation(DeleteMutationMixin, DjangoModelFormMutation):
    class Meta(DeleteMutationMixin.Meta):
        form_class = DeleteCourseForm

    @staticmethod
    def get_success_message() -> str:
        return Messages.COURSE_DELETED


class Query(graphene.ObjectType):
    search_courses = graphene.Field(
        PaginatedCourseObjectType,
        course_name=graphene.String(),
        course_code=graphene.String(),
        subject=graphene.ID(),
        school=graphene.ID(),
        school_type=graphene.ID(),
        country=graphene.ID(),
        city=graphene.ID(),
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
    )

    courses = graphene.List(CourseObjectType, school=graphene.ID())
    course = graphene.Field(CourseObjectType, id=graphene.ID())

    @login_required
    def resolve_search_courses(
        self,
        info: ResolveInfo,
        course_name: Optional[str] = None,
        course_code: Optional[str] = None,
        subject: ID = None,
        school: ID = None,
        school_type: ID = None,
        country: ID = None,
        city: ID = None,
        page: int = 1,
        page_size: int = 10,
        ordering: CourseOrderingOption = "name",
    ) -> graphene.ObjectType:
        """Filter courses based on the query parameters."""

        qs = Course.objects.all()

        if course_name is not None:
            qs = qs.filter(name__icontains=course_name)
        if course_code is not None:
            qs = qs.filter(code__icontains=course_code)
        if subject is not None:
            qs = qs.filter(subject__pk=subject)
        if school is not None:
            qs = qs.filter(school__pk=school)
        if school_type is not None:
            qs = qs.filter(school__school_type__pk=school_type)
        if country is not None:
            qs = qs.filter(school__city__country__pk=country)
        if city is not None:
            qs = qs.filter(school__city__pk=city)

        if ordering not in get_args(CourseOrderingOption):
            raise GraphQLError(GraphQLErrors.INVALID_ORDERING)

        if ordering not in {"name", "-name"}:
            # When ordering by score we also first order by the name.
            qs = qs.order_by("name")
        qs = qs.order_by(ordering)

        return get_paginator(qs, page_size, page, PaginatedCourseObjectType)

    @login_required
    def resolve_courses(
        self, info: ResolveInfo, school: ID = None,
    ) -> "QuerySet[Course]":
        qs = Course.objects.order_by("name")

        if school is not None:
            qs = qs.filter(school__pk=school)

        return qs

    @login_required
    def resolve_course(self, info: ResolveInfo, id: ID = None) -> Optional[Course]:
        return get_obj_or_none(Course, id)


class Mutation(graphene.ObjectType):
    create_course = CreateCourseMutation.Field()
    delete_course = DeleteCourseMutation.Field()
