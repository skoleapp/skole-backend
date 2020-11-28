from typing import Optional

import graphene
from django.conf import settings
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
        # We must manually call the translation function in order to perform the ordering based on the translated values.
        return City.objects.translated().order_by("translations__name")[
            : settings.AUTOCOMPLETE_MAX_RESULTS
        ]

    @staticmethod
    def resolve_city(root: None, info: ResolveInfo, id: ID = None) -> Optional[City]:
        return City.objects.get_or_none(pk=id)
