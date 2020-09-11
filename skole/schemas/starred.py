import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo

from skole.forms import CreateStarForm
from skole.models import Starred
from skole.schemas.mixins import SkoleCreateUpdateMutationMixin


class StarredObjectType(DjangoObjectType):
    class Meta:
        model = Starred


class StarredMutation(SkoleCreateUpdateMutationMixin, DjangoModelFormMutation):
    verification_required = True

    starred = graphene.Boolean()

    class Meta:
        form_class = CreateStarForm
        exclude_fields = ("id",)

    @classmethod
    def perform_mutate(
        cls, form: CreateStarForm, info: ResolveInfo
    ) -> "StarredMutation":
        assert info.context is not None
        # Not calling super (which saves the form), so that we don't
        # create two Starred instances here.
        starred = Starred.objects.perform_star(
            user=info.context.user, **form.cleaned_data
        )
        return cls(starred=bool(starred))


class Mutation(graphene.ObjectType):
    perform_star = StarredMutation.Field()
