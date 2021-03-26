from __future__ import annotations

from typing import cast

import graphene
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import CreateStarForm
from skole.models import Star, User
from skole.schemas.base import (
    SkoleCreateUpdateMutationMixin,
    SkoleDjangoObjectType,
    SkoleObjectType,
)
from skole.types import ResolveInfo


class StarObjectType(SkoleDjangoObjectType):
    class Meta:
        model = Star
        fields = ("id", "user", "course", "resource")


class StarMutation(SkoleCreateUpdateMutationMixin, DjangoModelFormMutation):
    """Start a course or a resource remove the star if it already exists."""

    verification_required = True
    starred = graphene.Boolean()

    class Meta:
        form_class = CreateStarForm
        exclude_fields = ("id",)

    @classmethod
    def perform_mutate(cls, form: CreateStarForm, info: ResolveInfo) -> StarMutation:
        # Not calling super (which saves the form) so that we don't create two Star instances here.
        star = Star.objects.create_or_delete_star(
            user=cast(User, info.context.user), target=form.cleaned_data["target"]
        )

        return cls(starred=bool(star))


class Mutation(SkoleObjectType):
    star = StarMutation.Field()
