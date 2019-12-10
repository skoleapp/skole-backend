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

    def resolve_cities(self, info: ResolveInfo) -> List[City]:
        return City.objects.all()
