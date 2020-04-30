import graphene
from graphene_django import DjangoObjectType

from skole.models import Badge


class BadgeObjectType(DjangoObjectType):
    name = graphene.String()
    description = graphene.String()

    class Meta:
        model = Badge
        fields = ("id", "name", "description")
