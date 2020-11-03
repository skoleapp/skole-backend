import graphene
from graphene_django import DjangoObjectType

from skole.models import Badge
from skole.utils import api_descriptions


class BadgeObjectType(DjangoObjectType):
    name = graphene.String()
    description = graphene.String()

    class Meta:
        model = Badge
        description = api_descriptions.BADGE_OBJECT_TYPE
        fields = ("id", "name", "description")
