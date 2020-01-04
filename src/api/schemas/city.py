from typing import List, Optional
import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo
from app.models import City


class CityType(DjangoObjectType):
    class Meta:
        model = City
        fields = ("id", "name")


class Query(graphene.ObjectType):
    cities = graphene.List(CityType)
    city = graphene.Field(CityType, city_id=graphene.Int())

    def resolve_cities(self, info: ResolveInfo) -> List[City]:
        return City.objects.order_by("name")

    def resolve_city(self, info: ResolveInfo, city_id: Optional[int] = None) -> City:
        try:
            return City.objects.get(pk=city_id)
        except City.DoesNotExist:
            """Return 'None' instead of throwing a GraphQL Error."""
            return None