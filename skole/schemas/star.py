from __future__ import annotations

from typing import cast

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import CreateStarForm
from skole.models import Star, User
from skole.schemas.mixins import SkoleCreateUpdateMutationMixin
from skole.types import ResolveInfo
from skole.utils import api_descriptions


class StarObjectType(DjangoObjectType):
    class Meta:
        model = Star
        description = api_descriptions.STAR_OBJECT_TYPE


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


class Mutation(graphene.ObjectType):
    star = StarMutation.Field(description=api_descriptions.STAR)
