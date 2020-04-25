import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo

from skole.forms.starred import StarForm
from skole.models import Starred
from skole.utils.decorators import verification_required_mutation


class StarredObjectType(DjangoObjectType):
    class Meta:
        model = Starred


class StarredMutation(DjangoModelFormMutation):
    starred = graphene.Boolean()

    class Meta:
        form_class = StarForm
        exclude_fields = ("id",)

    @classmethod
    @verification_required_mutation
    def perform_mutate(cls, form: StarForm, info: ResolveInfo) -> "StarredMutation":
        assert info.context is not None
        starred = Starred.objects.perform_star(
            user=info.context.user, **form.cleaned_data
        )

        starred_bool = starred is not None
        return cls(starred=starred_bool)


class Mutation(graphene.ObjectType):
    perform_star = StarredMutation.Field()
