from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from skole.models import City
from skole.utils.shortcuts import get_obj_or_none


class CityObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = City
        fields = ("id", "name")


class Query(graphene.ObjectType):
    cities = graphene.List(CityObjectType)
    city = graphene.Field(CityObjectType, id=graphene.ID())

    @login_required
    def resolve_cities(self, info: ResolveInfo) -> "QuerySet[City]":
        assert info.context is not None
        return City.objects.translated(info.context.LANGUAGE_CODE).order_by(
            "translations__name"
        )

    @login_required
    def resolve_city(
        self, info: ResolveInfo, id: Optional[int] = None
    ) -> Optional[City]:
        return get_obj_or_none(City, id)