from typing import List, Optional
import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo
from app.models import Country


class CountryType(DjangoObjectType):
    class Meta:
        model = Country
        fields = ("id", "name")


class Query(graphene.ObjectType):
    countries = graphene.List(CountryType)

    def resolve_countries(self, info: ResolveInfo) -> List[Country]:
        return Country.objects.all()
