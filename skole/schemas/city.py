from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType

from skole.models import City
from skole.types import ID, ResolveInfo


class CityObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = City
        fields = ("id", "name")


class Query(graphene.ObjectType):
    autocomplete_cities = graphene.List(CityObjectType)
    city = graphene.Field(CityObjectType, id=graphene.ID())

    @staticmethod
    def resolve_autocomplete_cities(root: None, info: ResolveInfo) -> QuerySet[City]:
        """
        Used for queries made by the client's auto complete fields.

        We want to avoid making massive queries by limiting the amount of results.
        """
        # We must manually call the translation function in order to perform the ordering based on the translated values.
        return City.objects.translated().order_by("translations__name")

    @staticmethod
    def resolve_city(root: None, info: ResolveInfo, id: ID = None) -> Optional[City]:
        return City.objects.get_or_none(pk=id)
