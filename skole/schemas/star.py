from __future__ import annotations

from typing import cast

import graphene
from django.conf import settings
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import CreateStarForm
from skole.models import Course, Resource, Star, User
from skole.schemas.course import PaginatedCourseObjectType
from skole.schemas.mixins import SkoleCreateUpdateMutationMixin
from skole.schemas.resource import PaginatedResourceObjectType
from skole.types import ResolveInfo
from skole.utils.api_descriptions import APIDescriptions
from skole.utils.pagination import get_paginator


class StarObjectType(DjangoObjectType):
    class Meta:
        model = Star
        description = APIDescriptions.STAR_OBJECT_TYPE


class StarMutation(SkoleCreateUpdateMutationMixin, DjangoModelFormMutation):
    verification_required = True
    star = graphene.Boolean()

    class Meta:
        form_class = CreateStarForm
        exclude_fields = ("id",)

    @classmethod
    def perform_mutate(cls, form: CreateStarForm, info: ResolveInfo) -> StarMutation:
        # Not calling super (which saves the form) so that we don't create two Star instances here.
        star = Star.objects.create_or_delete_star(
            user=cast(User, info.context.user), target=form.cleaned_data["target"]
        )

        return cls(star=bool(star))


class Query(graphene.ObjectType):
    starred_courses = graphene.Field(
        PaginatedCourseObjectType,
        user=graphene.ID(),
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
        description=APIDescriptions.STARRED_COURSES,
    )

    starred_resources = graphene.Field(
        PaginatedResourceObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
        description=APIDescriptions.STARRED_RESOURCES,
    )

    @staticmethod
    def resolve_starred_courses(
        root: None,
        info: ResolveInfo,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> QuerySet[Course]:
        qs = Course.objects.filter(stars__user__pk=info.context.user.pk)
        return get_paginator(qs, page_size, page, PaginatedCourseObjectType)

    @staticmethod
    def resolve_starred_resources(
        root: None,
        info: ResolveInfo,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> QuerySet[Resource]:
        qs = Resource.objects.filter(stars__user__pk=info.context.user.pk)
        return get_paginator(qs, page_size, page, PaginatedResourceObjectType)


class Mutation(graphene.ObjectType):
    star = StarMutation.Field(description=APIDescriptions.STAR)
