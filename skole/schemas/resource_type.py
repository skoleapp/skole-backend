import graphene
from django.conf import settings
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
    resource_types = graphene.List(ResourceTypeObjectType)
    autocomplete_resource_types = graphene.List(ResourceTypeObjectType)
    # Querying a single ResourceType is not needed.

    def resolve_resource_types(self, info: ResolveInfo) -> QuerySet[ResourceType]:
        return ResourceType.objects.all()

    def resolve_autocomplete_resource_types(
        self, info: ResolveInfo
    ) -> QuerySet[ResourceType]:
        """
        Used for queries made by the client's auto complete fields.

        We want to avoid making massive queries by limiting the amount of results.
        """
        return ResourceType.objects.all()[: settings.AUTOCOMPLETE_MAX_RESULTS]
