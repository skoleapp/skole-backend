import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from app.models import ResourceType


class ResourceTypeObjectType(DjangoObjectType):
    class Meta:
        model = ResourceType
        fields = ("id", "name")


class Query(graphene.ObjectType):
    resource_types = graphene.List(ResourceTypeObjectType)

    def resolve_resource_types(self, info: ResolveInfo) -> "QuerySet[ResourceType]":
        return ResourceType.objects.all()
