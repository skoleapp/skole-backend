from api.schemas.user import UserTypePublic
from typing import List

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from app.models import Resource


class ResourceType(DjangoObjectType):
    creator = graphene.Field(UserTypePublic)

    class Meta:
        model = Resource
        fields = ("id", "resource_type", "title", "file", "date", "course", "creator", "points", "modified", "created")


class Query(graphene.ObjectType):
    resource = graphene.Field(ResourceType, resource_id=graphene.Int(required=True))

    def resolve_resource(self, info: ResolveInfo, resource_id: str) -> Resource:
        return Resource.objects.get(pk=resource_id)
