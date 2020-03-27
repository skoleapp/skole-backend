from typing import Literal, Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import GraphQLError, ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.course import CreateCourseForm, DeleteCourseForm
from api.utils.common import get_obj_or_none
from api.utils.mixins import DeleteMutationMixin
from api.utils.pagination import PaginationMixin, get_paginator
from api.utils.star import StarMixin
from api.utils.vote import VoteMixin
from core.models import Course


class CourseObjectType(VoteMixin, StarMixin, DjangoObjectType):
    resource_count = graphene.Int()

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


class DeleteCourseMutation(DeleteMutationMixin, DjangoModelFormMutation):
    class Meta(DeleteMutationMixin.Meta):
        form_class = DeleteCourseForm


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

    courses = graphene.List(CourseObjectType)
    course = graphene.Field(CourseObjectType, id=graphene.ID())

    @login_required
    def resolve_search_courses(
        self,
        info: ResolveInfo,
        course_name: Optional[str] = None,
        course_code: Optional[str] = None,
        subject: Optional[int] = None,
        school: Optional[int] = None,
        school_type: Optional[int] = None,
        country: Optional[int] = None,
        city: Optional[int] = None,
        page: int = 1,
        page_size: int = 10,
        ordering: Optional[Literal["name", "-name", "points", "-points"]] = None,
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

        if ordering is not None and ordering not in {
            "name",
            "-name",
            "points",
            "-points",
        }:
            raise GraphQLError("Invalid ordering value.")

        if ordering in {"name", "-name"}:
            qs = qs.order_by(ordering)
        elif ordering == "points":
            # Ignore: qs changes from QuerySet to a List, get_paginator handles that.
            qs = sorted(qs, key=lambda c: c.points)  # type: ignore[assignment]
        else:  # -points
            # Ignore: Same as above.
            qs = sorted(qs, key=lambda c: c.points, reverse=True)  # type: ignore[assignment]

        return get_paginator(qs, page_size, page, PaginatedCourseObjectType)

    @login_required
    def resolve_courses(self, info: ResolveInfo) -> "QuerySet[Course]":
        return self.courses.order_by("name")

    @login_required
    def resolve_course(
        self, info: ResolveInfo, id: Optional[int] = None
    ) -> Optional[Course]:
        return get_obj_or_none(Course, id)


class Mutation(graphene.ObjectType):
    create_course = CreateCourseMutation.Field()
    delete_course = DeleteCourseMutation.Field()
