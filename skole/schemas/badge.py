import graphene

from skole.models import Badge
from skole.schemas.base import SkoleDjangoObjectType


class BadgeObjectType(SkoleDjangoObjectType):
    name = graphene.NonNull(graphene.String)
    description = graphene.NonNull(graphene.String)

    class Meta:
        model = Badge
        fields = ("id", "name", "description", "tier")
