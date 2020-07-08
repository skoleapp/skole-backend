import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo

from skole.forms.activity import MarkActivityReadForm
from skole.models import Activity
from skole.utils.constants import MutationErrors
from skole.utils.mixins import LoginRequiredMutationMixin


class ActivityObjectType(DjangoObjectType):
    name = graphene.String()
    description = graphene.String()
    read = graphene.Boolean()

    class Meta:
        model = Activity
        fields = ("name", "description", "read", "target_user", "course", "resource", "comment")

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
    def perform_mutate(cls, form: MarkActivityReadForm, info: ResolveInfo) -> "MarkActivityReadMutation":
        assert info.context is not None
        instance = form.instance

        if instance.user != info.context.user:
            return cls(errors=MutationErrors.NOT_OWNER)


        activity = Activity.objects.mark_read(activity=instance, **form.cleaned_data)
        return cls(activity=activity)


class Mutation(graphene.ObjectType):
    mark_activity_read = MarkActivityReadMutation.Field()
