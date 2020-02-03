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
    class Meta:
        form_class = CreateVoteForm

    @classmethod
    @login_required
    def perform_mutate(cls, form: CreateVoteForm, info: ResolveInfo) -> "VoteMutation":
        vote = Vote.objects.create_vote(user=info.context.user, **form.cleaned_data)
        return cls(vote=vote)


class Mutation(graphene.ObjectType):
    vote = VoteMutation.Field()
