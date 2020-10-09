from __future__ import annotations

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo

from skole.forms import CreateVoteForm
from skole.models import Vote
from skole.schemas.mixins import SkoleCreateUpdateMutationMixin


class VoteObjectType(DjangoObjectType):
    status = graphene.Int()

    class Meta:
        model = Vote
        fields = ("id", "user", "status", "comment", "course", "resource")


class VoteMutation(SkoleCreateUpdateMutationMixin, DjangoModelFormMutation):
    verification_required = True
    target_score = graphene.Int()

    class Meta:
        form_class = CreateVoteForm
        exclude_fields = ("id",)

    @classmethod
    def perform_mutate(cls, form: CreateVoteForm, info: ResolveInfo) -> VoteMutation:
        assert info.context is not None
        # Not calling super (which saves the form), so that we don't
        # create two Vote instances here.
        vote, target_score = Vote.objects.perform_vote(
            user=info.context.user,
            status=form.cleaned_data["status"],
            target=form.cleaned_data["target"],
        )

        return cls(vote=vote, target_score=target_score)


class Mutation(graphene.ObjectType):
    perform_vote = VoteMutation.Field()
