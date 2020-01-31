from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.utils.common import get_obj_or_none
from app.models import City


class CityObjectType(DjangoObjectType):
    class Meta:
        model = City
        fields = ("id", "name")


class Query(graphene.ObjectType):
    cities = graphene.List(CityObjectType)
    city = graphene.Field(CityObjectType, city_id=graphene.Int())

    def resolve_cities(self, info: ResolveInfo) -> List[City]:
        return City.objects.order_by("name")

    def resolve_city(
        self, info: ResolveInfo, city_id: Optional[int] = None
    ) -> Optional[City]:
        return get_obj_or_none(City, city_id)
