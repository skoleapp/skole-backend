import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.vote import CreateVoteForm
from app.models import Vote


class VoteObjectType(DjangoObjectType):
    status = graphene.Int()

    class Meta:
        model = Vote
        fields = ("id", "user", "status", "comment", "course", "resource")


class VoteMutation(DjangoModelFormMutation):
    target_points = graphene.Int()

    class Meta:
        form_class = CreateVoteForm
        exclude_fields = ("id",)

    @classmethod
    @login_required
    def perform_mutate(cls, form: CreateVoteForm, info: ResolveInfo) -> "VoteMutation":
        vote, target_points = Vote.objects.perform_vote(
            user=info.context.user, **form.cleaned_data
        )
        return cls(vote=vote, target_points=target_points)


class Mutation(graphene.ObjectType):
    perform_vote = VoteMutation.Field()
