import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.utils.points import get_points_for_target, POINTS_RESOURCE_MULTIPLIER
from api.utils.vote import AbstractUpvoteMutation, AbstractDownvoteMutation
from app.models import Resource


class ResourceType(DjangoObjectType):
    resource_type = graphene.String()
    points = graphene.Int()

    class Meta:
        model = Resource
        fields = ("id", "resource_type", "title", "file", "date", "creator", "points", "resource_part", "modified", "created")

    def resolve_points(self, info: ResolveInfo) -> int:
        return get_points_for_target(self, POINTS_RESOURCE_MULTIPLIER)


class UpvoteResourceMutation(AbstractUpvoteMutation):
    class Input:
        resource_id = graphene.Int()

    resource = graphene.Field(ResourceType)


class DownvoteResourceMutation(AbstractDownvoteMutation):
    class Input:
        resource_id = graphene.Int()

    resource = graphene.Field(ResourceType)


class Query(graphene.ObjectType):
    resource = graphene.Field(ResourceType, resource_id=graphene.Int(required=True))

    def resolve_resource(self, info: ResolveInfo, resource_id: str) -> Resource:
        return Resource.objects.get(pk=resource_id)


class Mutation(graphene.ObjectType):
    upvote_resource = UpvoteResourceMutation.Field()
    downvote_resource = DownvoteResourceMutation.Field()
