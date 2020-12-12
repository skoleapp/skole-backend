from typing import Optional

import graphene
from django.db.models import QuerySet

from skole.models import Country
from skole.schemas.base import SkoleDjangoObjectType, SkoleObjectType
from skole.types import ID, ResolveInfo


class CountryObjectType(SkoleDjangoObjectType):
    name = graphene.String()

    class Meta:
        model = Country
        fields = ("id", "name")


class Query(SkoleObjectType):
    autocomplete_countries = graphene.List(CountryObjectType)
    country = graphene.Field(CountryObjectType, id=graphene.ID())

    @staticmethod
    def resolve_autocomplete_countries(
        root: None, info: ResolveInfo
    ) -> QuerySet[Country]:
        """Results are sorted alphabetically."""
        # We must manually call the translation function in order to perform the ordering based on the translated values.
        return Country.objects.translated().order_by("translations__name")

    @staticmethod
    def resolve_country(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[Country]:
        return Country.objects.get_or_none(pk=id)
