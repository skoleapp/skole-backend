from __future__ import annotations

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphene_django.types import ErrorType
from graphql import ResolveInfo

from skole.forms import MarkActivityReadForm
from skole.models import Activity
from skole.schemas.mixins import SkoleCreateUpdateMutationMixin
from skole.types import JsonDict


class ActivityObjectType(DjangoObjectType):
    description = graphene.String()
    read = graphene.Boolean()

    class Meta:
        model = Activity
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


class MarkActivityReadMutation(SkoleCreateUpdateMutationMixin, DjangoModelFormMutation):
    """Mark a single activity read/unread and return the updated activity."""

    login_required = True

    activity = graphene.Field(ActivityObjectType)

    class Meta:
        form_class = MarkActivityReadForm


class MarkAllActivitiesReadMutation(SkoleCreateUpdateMutationMixin, graphene.Mutation):
    """Mark all activities of the given user as read."""

    login_required = True

    activities = graphene.List(ActivityObjectType)
    errors = graphene.List(ErrorType)

    @classmethod
    def mutate(
        cls, root: None, info: ResolveInfo, **input: JsonDict
    ) -> MarkAllActivitiesReadMutation:
        assert info.context is not None
        activities = Activity.objects.mark_all_as_read(user=info.context.user)
        return cls(activities=activities)


class Mutation(graphene.ObjectType):
    mark_activity_read = MarkActivityReadMutation.Field()
    mark_all_activities_read = MarkAllActivitiesReadMutation.Field()
