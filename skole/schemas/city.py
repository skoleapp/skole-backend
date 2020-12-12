from typing import Optional

import graphene
from django.db.models import QuerySet

from skole.models import City
from skole.schemas.base import SkoleDjangoObjectType, SkoleObjectType
from skole.types import ID, ResolveInfo


class CityObjectType(SkoleDjangoObjectType):
    name = graphene.String()

    class Meta:
        model = City
        fields = ("id", "name")


class Query(SkoleObjectType):
    autocomplete_cities = graphene.List(CityObjectType)
    city = graphene.Field(CityObjectType, id=graphene.ID())

    @staticmethod
    def resolve_autocomplete_cities(root: None, info: ResolveInfo) -> QuerySet[City]:
        """Results are sorted alphabetically."""
        return City.objects.translated().order_by("translations__name")

    @staticmethod
    def resolve_city(root: None, info: ResolveInfo, id: ID = None) -> Optional[City]:
        return City.objects.get_or_none(pk=id)
