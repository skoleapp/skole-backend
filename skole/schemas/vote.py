from __future__ import annotations

from typing import cast

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import CreateVoteForm
from skole.models import User, Vote
from skole.schemas.mixins import SkoleCreateUpdateMutationMixin
from skole.types import ResolveInfo
from skole.utils import api_descriptions


class VoteObjectType(DjangoObjectType):
    status = graphene.Int()

    class Meta:
        model = Vote
        description = api_descriptions.VOTE_OBJECT_TYPE
        fields = ("id", "user", "status", "comment", "course", "resource")


class VoteMutation(SkoleCreateUpdateMutationMixin, DjangoModelFormMutation):
    verification_required = True
    target_score = graphene.Int()

    class Meta:
        form_class = CreateVoteForm
        exclude_fields = ("id",)

    @classmethod
    def perform_mutate(cls, form: CreateVoteForm, info: ResolveInfo) -> VoteMutation:
        # Not calling super (which saves the form), so that we don't
        # create two Vote instances here.
        vote, target_score = Vote.objects.perform_vote(
            user=cast(User, info.context.user),
            status=form.cleaned_data["status"],
            target=form.cleaned_data["target"],
        )

        return cls(vote=vote, target_score=target_score)


class Mutation(graphene.ObjectType):
    perform_vote = VoteMutation.Field(description=api_descriptions.VOTE)
