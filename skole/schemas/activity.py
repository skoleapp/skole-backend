from __future__ import annotations

from typing import cast

import graphene
from django.conf import settings
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphene_django.types import ErrorType
from graphql_jwt.decorators import login_required

from skole.forms import MarkActivityAsReadForm
from skole.models import Activity, User
from skole.schemas.mixins import PaginationMixin, SkoleCreateUpdateMutationMixin
from skole.types import JsonDict, ResolveInfo
from skole.utils import api_descriptions
from skole.utils.pagination import get_paginator


class ActivityObjectType(DjangoObjectType):
    description = graphene.String()
    read = graphene.Boolean()

    class Meta:
        model = Activity
        description = api_descriptions.ACTIVITY_OBJECT_TYPE
        fields = (
            "id",
            "description",
            "read",
            "target_user",
            "course",
            "resource",
            "comment",
        )

    @staticmethod
    def resolve_name(root: Activity, info: ResolveInfo) -> str:
        return root.activity_type.name

    @staticmethod
    def resolve_description(root: Activity, info: ResolveInfo) -> str:
        return root.activity_type.description


class PaginatedActivityObjectType(PaginationMixin, graphene.ObjectType):
    objects = graphene.List(ActivityObjectType)

    class Meta:
        description = api_descriptions.PAGINATED_ACTIVITY_OBJECT_TYPE


class MarkActivityAsReadMutation(
    SkoleCreateUpdateMutationMixin, DjangoModelFormMutation
):
    login_required = True
    activity = graphene.Field(ActivityObjectType)

    class Meta:
        form_class = MarkActivityAsReadForm


class MarkAllActivitiesAsReadMutation(
    SkoleCreateUpdateMutationMixin, graphene.Mutation
):
    login_required = True
    activities = graphene.Field(PaginatedActivityObjectType)
    errors = graphene.List(ErrorType)

    @classmethod
    def mutate(
        cls, root: None, info: ResolveInfo, **input: JsonDict
    ) -> MarkAllActivitiesAsReadMutation:
        qs = Activity.objects.mark_all_as_read(user=cast(User, info.context.user))

        page_size = settings.DEFAULT_PAGE_SIZE
        page = 1
        activities = get_paginator(qs, page_size, page, PaginatedActivityObjectType)

        return cls(activities=activities)


class Mutation(graphene.ObjectType):
    mark_activity_as_read = MarkActivityAsReadMutation.Field(
        description=api_descriptions.MARK_ACTIVITY_AS_READ
    )

    mark_all_activities_as_read = MarkAllActivitiesAsReadMutation.Field(
        description=api_descriptions.MARK_ALL_ACTIVITIES_AS_READ
    )


class Query(graphene.ObjectType):
    activities = graphene.Field(
        PaginatedActivityObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        description=api_descriptions.ACTIVITY,
    )

    activity_preview = graphene.List(
        ActivityObjectType, description=api_descriptions.ACTIVITY_PREVIEW
    )

    @staticmethod
    @login_required
    def resolve_activities(
        root: None,
        info: ResolveInfo,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> PaginatedActivityObjectType:
        user = cast(User, info.context.user)
        qs = user.activities.all()
        return get_paginator(qs, page_size, page, PaginatedActivityObjectType)

    @staticmethod
    @login_required
    def resolve_activity_preview(root: None, info: ResolveInfo) -> QuerySet[Activity]:
        user = cast(User, info.context.user)
        return user.activities.all()[: settings.ACTIVITY_PREVIEW_COUNT]
