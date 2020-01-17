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
    country = graphene.Field(CountryType, country_id=graphene.Int())

    def resolve_countries(self, info: ResolveInfo) -> List[Country]:
        return Country.objects.order_by("name")

    def resolve_country(self, info: ResolveInfo, country_id: Optional[int] = None) -> Country:
        try:
            return Country.objects.get(pk=country_id)
        except Country.DoesNotExist:
            """Return 'None' instead of throwing a GraphQL Error."""
            return None
