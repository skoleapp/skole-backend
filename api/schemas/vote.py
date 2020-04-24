import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo

from api.forms.vote import CreateVoteForm
from api.utils.decorators import verification_required_mutation
from core.models.vote import Vote


class VoteObjectType(DjangoObjectType):
    status = graphene.Int()

    class Meta:
        model = Vote
        fields = ("id", "user", "status", "comment", "course", "resource")


class VoteMutation(DjangoModelFormMutation):
    target_score = graphene.Int()

    class Meta:
        form_class = CreateVoteForm
        exclude_fields = ("id",)

    @classmethod
    @verification_required_mutation
    def perform_mutate(cls, form: CreateVoteForm, info: ResolveInfo) -> "VoteMutation":
        assert info.context is not None
        vote, target_score = Vote.objects.perform_vote(
            user=info.context.user, **form.cleaned_data
        )
        return cls(vote=vote, target_score=target_score)


class Mutation(graphene.ObjectType):
    perform_vote = VoteMutation.Field()
