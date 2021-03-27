import graphene
from django.db.models import QuerySet

from skole.models import Badge
from skole.overridden import verification_required
from skole.schemas.base import SkoleDjangoObjectType, SkoleObjectType
from skole.types import ResolveInfo


class BadgeObjectType(SkoleDjangoObjectType):
    name = graphene.NonNull(graphene.String)
    description = graphene.NonNull(graphene.String)

    class Meta:
        model = Badge
        fields = ("id", "name", "description", "tier")


class Query(SkoleObjectType):
    badges = graphene.List(BadgeObjectType)

    @staticmethod
    @verification_required
    def resolve_badges(root: None, info: ResolveInfo) -> QuerySet[Badge]:
        return Badge.objects.all()
