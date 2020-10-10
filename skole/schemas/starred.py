from __future__ import annotations

from typing import cast

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import CreateStarForm
from skole.models import Starred, User
from skole.schemas.mixins import SkoleCreateUpdateMutationMixin
from skole.types import ResolveInfo


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
    def perform_mutate(cls, form: CreateStarForm, info: ResolveInfo) -> StarredMutation:
        # Not calling super (which saves the form), so that we don't
        # create two Starred instances here.
        starred = Starred.objects.perform_star(
            user=cast(User, info.context.user), target=form.cleaned_data["target"]
        )
        return cls(starred=bool(starred))


class Mutation(graphene.ObjectType):
    perform_star = StarredMutation.Field()
