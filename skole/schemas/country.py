from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import Country
from skole.types import ID


class CountryObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = Country
        fields = ("id", "name")


class Query(graphene.ObjectType):
    autocomplete_countries = graphene.List(CountryObjectType)
    country = graphene.Field(CountryObjectType, id=graphene.ID())

    def resolve_autocomplete_countries(self, info: ResolveInfo) -> QuerySet[Country]:
        """
        Used for queries made by the client's auto complete fields.

        We want to avoid making massive queries by limiting the amount of results.
        """
        assert info.context is not None
        # We must manually call the translation function in order to perform the ordering based on the translated values.
        return Country.objects.translated().order_by("translations__name")

    def resolve_country(self, info: ResolveInfo, id: ID = None) -> Optional[Country]:
        return Country.objects.get_or_none(pk=id)
