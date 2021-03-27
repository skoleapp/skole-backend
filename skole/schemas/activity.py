from __future__ import annotations

from typing import cast

import graphene
from django.conf import settings
from django.db.models import QuerySet
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphene_django.types import ErrorType

from skole.forms import MarkActivityAsReadForm
from skole.models import Activity, User
from skole.overridden import verification_required
from skole.schemas.base import (
    SkoleCreateUpdateMutationMixin,
    SkoleDjangoObjectType,
    SkoleObjectType,
)
from skole.schemas.mixins import PaginationMixin
from skole.types import JsonDict, ResolveInfo
from skole.utils.pagination import get_paginator


class ActivityObjectType(SkoleDjangoObjectType):
    description = graphene.String()
    read = graphene.Boolean()

    class Meta:
        model = Activity
        fields = (
            "id",
            "description",
            "read",
            "causing_user",
            "comment",
            "badge_progress",
        )

    @staticmethod
    def resolve_identifier(root: Activity, info: ResolveInfo) -> str:
        return root.activity_type.identifier

    @staticmethod
    def resolve_description(root: Activity, info: ResolveInfo) -> str:
        if root.badge_progress:
            return root.activity_type.description.format(root.badge_progress.badge)
        return root.activity_type.description


class PaginatedActivityObjectType(PaginationMixin, SkoleObjectType):
    objects = graphene.List(ActivityObjectType)

    class Meta:
        description = Activity.__doc__


class MarkActivityAsReadMutation(
    SkoleCreateUpdateMutationMixin, DjangoModelFormMutation
):
    """Mark a single activity read/unread."""

    verification_required = True
    activity = graphene.Field(ActivityObjectType)

    class Meta:
        form_class = MarkActivityAsReadForm


class MarkAllActivitiesAsReadMutation(
    SkoleCreateUpdateMutationMixin, graphene.Mutation
):
    """Mark all activities of the given user as read."""

    verification_required = True
    activities = graphene.Field(PaginatedActivityObjectType)
    errors = graphene.List(ErrorType)

    @classmethod
    def mutate(
        cls, root: None, info: ResolveInfo, **input: JsonDict
    ) -> MarkAllActivitiesAsReadMutation:
        qs = Activity.objects.mark_all_as_read(
            user=cast(User, info.context.user)
        ).order_by("-pk")

        page_size = settings.DEFAULT_PAGE_SIZE
        page = 1
        activities = get_paginator(qs, page_size, page, PaginatedActivityObjectType)

        return cls(activities=activities)


class Mutation(SkoleObjectType):
    mark_activity_as_read = MarkActivityAsReadMutation.Field()
    mark_all_activities_as_read = MarkAllActivitiesAsReadMutation.Field()


class Query(SkoleObjectType):
    activities = graphene.Field(
        PaginatedActivityObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
    )

    activity_preview = graphene.List(ActivityObjectType)

    @staticmethod
    @verification_required
    def resolve_activities(
        root: None,
        info: ResolveInfo,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> PaginatedActivityObjectType:
        """
        Return all activity of to the user making the query.

        Results are sorted by creation time.
        """
        user = cast(User, info.context.user)
        qs = user.activities.order_by("-pk")
        return get_paginator(qs, page_size, page, PaginatedActivityObjectType)

    @staticmethod
    @verification_required
    def resolve_activity_preview(root: None, info: ResolveInfo) -> QuerySet[Activity]:
        """Return limited amount of activity of user making the query for a preview."""
        user = cast(User, info.context.user)
        return user.activities.order_by("-pk")[: settings.ACTIVITY_PREVIEW_COUNT]
