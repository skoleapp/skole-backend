import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.utils.points import get_points_for_resource
from api.utils.vote import AbstractUpvoteMutation, AbstractDownvoteMutation
from app.models import Resource


class ResourceType(DjangoObjectType):
    resource_type = graphene.String()
    points = graphene.Int()

    class Meta:
        model = Resource
        fields = ("id", "resource_type", "title", "file", "date", "creator", "points", "modified", "created")

    def resolve_points(self, info: ResolveInfo) -> int:
        return get_points_for_resource(self)


class UpvoteResourceMutation(AbstractUpvoteMutation):
    class Input:
        resource_id = graphene.Int()

    resource = graphene.Field(ResourceType)
    _target_model = ResourceType._meta.model


class DownvoteResourceMutation(AbstractDownvoteMutation):
    class Input:
        resource_id = graphene.Int()

    resource = graphene.Field(ResourceType)
    _target_model = ResourceType._meta.model


class Query(graphene.ObjectType):
    resource = graphene.Field(ResourceType, resource_id=graphene.Int(required=True))

    def resolve_resource(self, info: ResolveInfo, resource_id: str) -> Resource:
        return Resource.objects.get(pk=resource_id)


class Mutation(graphene.ObjectType):
    upvote_resource = UpvoteResourceMutation.Field()
    downvote_resource = DownvoteResourceMutation.Field()
