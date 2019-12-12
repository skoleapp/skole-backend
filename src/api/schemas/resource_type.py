from typing import List

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from app.models import ResourceType


class ResourceTypeObjectType(DjangoObjectType):
    class Meta:
        model = ResourceType
        fields = ("id", "name", "has_parts")


class Query(graphene.ObjectType):
    resource_types = graphene.List(ResourceTypeObjectType)

    def resolve_resource_types(self, info: ResolveInfo) -> List[ResourceType]:
        return ResourceType.objects.all()
