from typing import Optional

import graphene

from skole.models import BadgeProgress
from skole.schemas.base import SkoleDjangoObjectType
from skole.types import ResolveInfo


class BadgeProgressObjectType(SkoleDjangoObjectType):

    # It would be nice to be able flatten the fields from `badge` here, but the `tier`
    # field is problematic, since it automatically becomes an Enum from the model field
    # in the `BadgeObjectType`, so specifying it here would be non-trivial.
    # We do flatten the `steps` field though, since it's just more logical in the
    # frontend that `progress` and `steps` are queryable on the same object.
    steps = graphene.Int()

    class Meta:
        model = BadgeProgress
        fields = ("user", "badge", "progress", "steps")

    @staticmethod
    def resolve_steps(root: BadgeProgress, info: ResolveInfo) -> Optional[int]:
        return root.badge.steps
