from typing import Optional

import graphene
from django.conf import settings
from django.db.models import QuerySet
from graphene_django import DjangoObjectType

from skole.models import City
from skole.types import ID, ResolveInfo
from skole.utils import api_descriptions


class CityObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = City
        description = api_descriptions.CITY_OBJECT_TYPE
        fields = ("id", "name")


class Query(graphene.ObjectType):
    autocomplete_cities = graphene.List(
        CityObjectType, description=api_descriptions.AUTOCOMPLETE_CITIES,
    )

    city = graphene.Field(
        CityObjectType, id=graphene.ID(), description=api_descriptions.DETAIL_QUERY,
    )

    @staticmethod
    def resolve_autocomplete_cities(root: None, info: ResolveInfo) -> QuerySet[City]:
        # We must manually call the translation function in order to perform the ordering based on the translated values.
        return City.objects.translated().order_by("translations__name")[
            : settings.AUTOCOMPLETE_MAX_RESULTS
        ]

    @staticmethod
    def resolve_city(root: None, info: ResolveInfo, id: ID = None) -> Optional[City]:
        return City.objects.get_or_none(pk=id)
