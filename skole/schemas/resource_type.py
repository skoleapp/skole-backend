import graphene
from django.db.models import QuerySet

from skole.models import ResourceType
from skole.schemas.base import SkoleDjangoObjectType, SkoleObjectType
from skole.types import ResolveInfo


class ResourceTypeObjectType(SkoleDjangoObjectType):
    name = graphene.String()

    class Meta:
        model = ResourceType
        fields = ("id", "name")


class Query(SkoleObjectType):
    resource_types = graphene.List(ResourceTypeObjectType)
    autocomplete_resource_types = graphene.List(ResourceTypeObjectType)

    # Querying a single ResourceType is not needed.

    @staticmethod
    def resolve_resource_types(root: None, info: ResolveInfo) -> QuerySet[ResourceType]:
        """
        Return unlimited amount of resource types.

        Results are sorted by creation time.
        """
        return ResourceType.objects.all()

    @staticmethod
    def resolve_autocomplete_resource_types(
        root: None, info: ResolveInfo
    ) -> QuerySet[ResourceType]:
        """Results are sorted alphabetically."""
        # We must manually call the translation function in order to perform the ordering based on the translated values.
        return ResourceType.objects.translated()
