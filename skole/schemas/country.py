from typing import Optional

import graphene
from django.conf import settings
from django.db.models import QuerySet
from graphene_django import DjangoObjectType

from skole.models import Country
from skole.types import ID, ResolveInfo
from skole.utils.api_descriptions import APIDescriptions


class CountryObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = Country
        description = APIDescriptions.COUNTRY_OBJECT_TYPE
        fields = ("id", "name")


class Query(graphene.ObjectType):
    autocomplete_countries = graphene.List(
        CountryObjectType, description=APIDescriptions.AUTOCOMPLETE_QUERY,
    )

    country = graphene.Field(
        CountryObjectType, id=graphene.ID(), description=APIDescriptions.DETAIL_QUERY,
    )

    @staticmethod
    def resolve_autocomplete_countries(
        root: None, info: ResolveInfo
    ) -> QuerySet[Country]:
        # We must manually call the translation function in order to perform the ordering based on the translated values.
        return Country.objects.translated().order_by("translations__name")[
            : settings.AUTOCOMPLETE_MAX_RESULTS
        ]

    @staticmethod
    def resolve_country(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[Country]:
        return Country.objects.get_or_none(pk=id)
