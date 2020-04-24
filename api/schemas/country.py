from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.utils.common import get_obj_or_none
from api.utils.decorators import login_required
from core.models import Country


class CountryObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = Country
        fields = ("id", "name")


class Query(graphene.ObjectType):
    countries = graphene.List(CountryObjectType)
    country = graphene.Field(CountryObjectType, id=graphene.ID())

    @login_required
    def resolve_countries(self, info: ResolveInfo) -> "QuerySet[Country]":
        assert info.context is not None
        return Country.objects.translated(info.context.LANGUAGE_CODE).order_by(
            "translations__name"
        )

    @login_required
    def resolve_country(
        self, info: ResolveInfo, id: Optional[int] = None
    ) -> Optional[Country]:
        return get_obj_or_none(Country, id)
