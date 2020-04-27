import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo

from skole.forms.vote import CreateVoteForm
from skole.models.vote import Vote
from skole.utils.constants import MutationErrors
from skole.utils.decorators import verification_required_mutation


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
        target = form.cleaned_data.get("target")

        if hasattr(target, "user") and target.user == info.context.user:
            return cls(errors=MutationErrors.VOTE_OWN_CONTENT)

        vote, target_score = Vote.objects.perform_vote(
            user=info.context.user, **form.cleaned_data
        )

        return cls(vote=vote, target_score=target_score)


class Mutation(graphene.ObjectType):
    perform_vote = VoteMutation.Field()
