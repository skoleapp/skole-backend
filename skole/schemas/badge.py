import graphene
from graphene_django import DjangoObjectType

from skole.models import Badge
from skole.utils.api_descriptions import APIDescriptions


class BadgeObjectType(DjangoObjectType):
    name = graphene.String()
    description = graphene.String()

    class Meta:
        model = Badge
        description = APIDescriptions
        fields = ("id", "name", "description")
