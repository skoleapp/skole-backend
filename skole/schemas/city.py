from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import City
from skole.types import ID
from skole.utils.shortcuts import get_obj_or_none


class CityObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = City
        fields = ("id", "name")


class Query(graphene.ObjectType):
    autocomplete_cities = graphene.List(CityObjectType)
    city = graphene.Field(CityObjectType, id=graphene.ID())

    def resolve_autocomplete_cities(self, info: ResolveInfo) -> "QuerySet[City]":
        """
        Used for queries made by the client's auto complete fields.

        We want to avoid making massive queries by limiting the amount of results.
        """
        assert info.context is not None
        # We must manually call the translation function in order to perform the ordering based on the translated values.
        return City.objects.translated().order_by("translations__name")

    def resolve_city(self, info: ResolveInfo, id: ID = None) -> Optional[City]:
        return get_obj_or_none(City, id)
