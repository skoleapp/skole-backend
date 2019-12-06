import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.schemas.user import UserTypePublic
from api.utils.points import POINTS_RESOURCE_UPVOTED, POINTS_RESOURCE_DOWNVOTED
from app.models import Resource


class ResourceType(DjangoObjectType):
    points = graphene.Int()
    creator = graphene.Field(UserTypePublic)

    class Meta:
        model = Resource
        fields = ("id", "resource_type", "title", "file", "date", "course", "creator", "points", "modified", "created")

        def resolve_points(self, info: ResolveInfo) -> int:
            points = 0
            points += self.upvotes * POINTS_RESOURCE_UPVOTED
            points += self.downvotes * POINTS_RESOURCE_DOWNVOTED
            return points


class Query(graphene.ObjectType):
    resource = graphene.Field(ResourceType, resource_id=graphene.Int(required=True))

    def resolve_resource(self, info: ResolveInfo, resource_id: str) -> Resource:
        return Resource.objects.get(pk=resource_id)
