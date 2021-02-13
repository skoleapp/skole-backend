from typing import Optional

import graphene
from django.db.models import QuerySet

from skole.models import Country
from skole.schemas.base import SkoleDjangoObjectType, SkoleObjectType
from skole.types import ResolveInfo


class CountryObjectType(SkoleDjangoObjectType):
    slug = graphene.String()
    name = graphene.NonNull(graphene.String)

    class Meta:
        model = Country
        fields = ("slug", "name")


class Query(SkoleObjectType):
    autocomplete_countries = graphene.List(CountryObjectType)
    country = graphene.Field(CountryObjectType, slug=graphene.String())

    @staticmethod
    def resolve_autocomplete_countries(
        root: None, info: ResolveInfo
    ) -> QuerySet[Country]:
        """Results are sorted alphabetically."""
        return Country.objects.translated().order_by("translations__name")

    @staticmethod
    def resolve_country(
        root: None, info: ResolveInfo, slug: str = ""
    ) -> Optional[Country]:
        return Country.objects.get_or_none(slug=slug)
