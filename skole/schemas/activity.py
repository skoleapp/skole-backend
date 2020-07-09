from typing import Any

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo

from skole.forms.activity import MarkActivityReadForm
from skole.models import Activity
from skole.utils.constants import MutationErrors
from skole.utils.mixins import FormErrorMixin, LoginRequiredMutationMixin


class ActivityObjectType(DjangoObjectType):
    name = graphene.String()
    description = graphene.String()
    read = graphene.Boolean()

    class Meta:
        model = Activity
        fields = (
            "name",
            "description",
            "read",
            "target_user",
            "course",
            "resource",
            "comment",
        )

    def resolve_name(self, info: ResolveInfo) -> str:
        return self.activity_type.name

    def resolve_description(self, info: ResolveInfo) -> str:
        return self.activity_type.description


class MarkActivityReadMutation(LoginRequiredMutationMixin, DjangoModelFormMutation):
    """Mark a single activity read/unread and return the updated activity."""

    activity = graphene.Field(ActivityObjectType)

    class Meta:
        form_class = MarkActivityReadForm

    @classmethod
    def perform_mutate(
        cls, form: MarkActivityReadForm, info: ResolveInfo
    ) -> "MarkActivityReadMutation":
        assert info.context is not None
        instance = form.instance

        if instance.user != info.context.user:
            return cls(errors=MutationErrors.NOT_OWNER)

        activity = Activity.objects.mark_read(activity=instance, **form.cleaned_data)
        return cls(activity=activity)


class MarkAllActivitiesReadMutation(
    LoginRequiredMutationMixin, FormErrorMixin, graphene.Mutation
):
    """Mark all activities of the given user as read."""

    activities = graphene.List(ActivityObjectType)

    # Ignore: Mypy expects the signature to match LoginRequiredMutationMixin's signature.
    @classmethod
    def mutate(cls, root: Any, info: ResolveInfo) -> "MarkAllActivitiesReadMutation":  # type: ignore[override]
        assert info.context is not None
        activities = Activity.objects.mark_all_as_read(user=info.context.user)
        return cls(activities=activities)


class Mutation(graphene.ObjectType):
    mark_activity_read = MarkActivityReadMutation.Field()
    mark_all_activities_read = MarkAllActivitiesReadMutation.Field()
