import graphene
from graphene_django import DjangoObjectType
from skole.models import Badge


class BadgeObjectType(DjangoObjectType):
    class Meta:
        model = Badge
        fields = ("id", "name", "description")
