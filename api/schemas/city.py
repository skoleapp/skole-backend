from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.utils.common import get_obj_or_none
from api.utils.decorators import login_required
from core.models import City


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
