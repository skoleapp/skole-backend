from __future__ import annotations

from typing import cast

import graphene
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import CreateVoteForm
from skole.models import User, Vote
from skole.schemas.base import (
    SkoleCreateUpdateMutationMixin,
    SkoleDjangoObjectType,
    SkoleObjectType,
)
from skole.types import ResolveInfo


class VoteObjectType(SkoleDjangoObjectType):
    class Meta:
        model = Vote
        fields = ("id", "user", "status", "comment", "course", "resource")


class VoteMutation(SkoleCreateUpdateMutationMixin, DjangoModelFormMutation):
    """Upvote, downvote or remove a vote from a course, resource or a comment."""

    verification_required = True
    target_score = graphene.NonNull(graphene.Int)

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


class Mutation(SkoleObjectType):
    vote = VoteMutation.Field()
