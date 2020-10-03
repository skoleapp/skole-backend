import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import ResourceType


class ResourceTypeObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = ResourceType
        fields = ("id", "name")


class Query(graphene.ObjectType):
    auto_complete_resource_types = graphene.List(ResourceTypeObjectType)

    # Querying a single ResourceType is not needed.

    def resolve_auto_complete_resource_types(
        self, info: ResolveInfo
    ) -> "QuerySet[ResourceType]":
        """Used for queries made by the client's auto complete fields."""
        return ResourceType.objects.all()
