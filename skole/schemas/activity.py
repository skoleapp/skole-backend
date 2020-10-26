from __future__ import annotations

from typing import cast

import graphene
from django.conf import settings
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphene_django.types import ErrorType

from skole.forms import MarkActivityAsReadForm
from skole.models import Activity, User
from skole.schemas.mixins import PaginationMixin, SkoleCreateUpdateMutationMixin
from skole.types import JsonDict, ResolveInfo
from skole.utils.api_descriptions import APIDescriptions
from skole.utils.decorators import private_field
from skole.utils.pagination import get_paginator


class ActivityObjectType(DjangoObjectType):
    description = graphene.String()
    read = graphene.Boolean()

    class Meta:
        model = Activity
        description = APIDescriptions.ACTIVITY_OBJECT_TYPE
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
        description = APIDescriptions.PAGINATED_ACTIVITY_OBJECT_TYPE


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
    activities = graphene.List(ActivityObjectType)
    errors = graphene.List(ErrorType)

    @classmethod
    def mutate(
        cls, root: None, info: ResolveInfo, **input: JsonDict
    ) -> MarkAllActivitiesAsReadMutation:
        activities = Activity.objects.mark_all_as_read(
            user=cast(User, info.context.user)
        )

        return cls(activities=activities)


class Mutation(graphene.ObjectType):
    mark_activity_as_read = MarkActivityAsReadMutation.Field(
        description=APIDescriptions.MARK_ACTIVITY_AS_READ
    )

    mark_all_activities_as_read = MarkAllActivitiesAsReadMutation.Field(
        description=APIDescriptions.MARK_ALL_ACTIVITIES_AS_READ
    )


class Query(graphene.ObjectType):
    activity = graphene.Field(
        PaginatedActivityObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
        description=APIDescriptions.ACTIVITY,
    )

    activity_preview = graphene.Field(ActivityObjectType)

    @staticmethod
    @private_field
    def resolve_activity(
        root: User,
        info: ResolveInfo,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> graphene.ObjectType:
        qs = root.activities.all()
        return get_paginator(qs, page_size, page, PaginatedActivityObjectType)

    def resolve_activity_preview(
        root: User, info: ResolveInfo
    ) -> QuerySet[ActivityObjectType]:
        # Ignore: Mypy cannot infer correct queryset typings from related manager.
        return root.activities.all()[: settings.ACTIVITY_PREVIEW_COUNT]  # type: ignore [return-value]
