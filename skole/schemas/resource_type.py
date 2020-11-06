import graphene
from django.conf import settings
from django.db.models import QuerySet
from graphene_django import DjangoObjectType

from skole.models import ResourceType
from skole.types import ResolveInfo
from skole.utils import api_descriptions


class ResourceTypeObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = ResourceType
        description = api_descriptions.RESOURCE_TYPE_OBJECT_TYPE
        fields = ("id", "name")


class Query(graphene.ObjectType):
    resource_types = graphene.List(
        ResourceTypeObjectType, description=api_descriptions.RESOURCE_TYPES,
    )

    autocomplete_resource_types = graphene.List(
        ResourceTypeObjectType,
        description=api_descriptions.AUTOCOMPLETE_RESOURCE_TYPES,
    )

    # Querying a single ResourceType is not needed.

    @staticmethod
    def resolve_resource_types(root: None, info: ResolveInfo) -> QuerySet[ResourceType]:
        return ResourceType.objects.all()

    @staticmethod
    def resolve_autocomplete_resource_types(
        root: None, info: ResolveInfo
    ) -> QuerySet[ResourceType]:
        # We must manually call the translation function in order to perform the ordering based on the translated values.
        return ResourceType.objects.translated().order_by("translations__name")[
            : settings.AUTOCOMPLETE_MAX_RESULTS
        ]
