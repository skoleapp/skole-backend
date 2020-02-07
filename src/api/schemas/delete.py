from typing import Any, Dict, Optional, Union

import graphene
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import GraphQLError, ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.vote import CreateVoteForm
from api.utils.messages import NOT_OWNER_MESSAGE
from app.models import Comment, Resource, ResourcePart, Vote


class DeleteObjectMutation(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        comment = graphene.Int()
        resource = graphene.Int()
        resource_part = graphene.Int()
        vote = graphene.Int()

    @classmethod
    @login_required
    def mutate(
        cls, root: Any, info: ResolveInfo, **kwargs: Dict[str, int]
    ) -> "DeleteObjectMutation":
        if len(kwargs) != 1:
            raise GraphQLError(_("Incorrect mutation arguments."))

        obj: Any
        pk: Any
        if pk := kwargs.get("comment_id"):
            obj = Comment.objects.get(pk=pk)
        elif pk := kwargs.get("resource_id"):
            obj = Resource.objects.get(pk=pk)
        elif pk := kwargs.get("resource_part_id"):
            obj = ResourcePart.objects.get(pk=pk)
        elif pk := kwargs.get("vote_id"):
            obj = Vote.objects.get(pk=pk)
        else:
            obj = None

        if hasattr(obj, "user") and obj.user != info.context.user:
            raise GraphQLError(NOT_OWNER_MESSAGE)

        obj.delete()
        return cls(message=_("Object deleted successfully!"))


class Mutation(graphene.ObjectType):
    delete_object = DeleteObjectMutation.Field()
