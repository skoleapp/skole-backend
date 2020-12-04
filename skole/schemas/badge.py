import graphene

from skole.models import Badge
from skole.schemas.base import SkoleDjangoObjectType


class BadgeObjectType(SkoleDjangoObjectType):
    name = graphene.String()
    description = graphene.String()

    class Meta:
        model = Badge
        fields = ("id", "name", "description")
