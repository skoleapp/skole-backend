from typing import Optional

import graphene
from graphql import ResolveInfo

from core.models import Course, Resource, Star


class StarMixin:
    starred = graphene.Boolean()

    def resolve_starred(self, info: ResolveInfo) -> Optional[int]:
        """Resolve whether user has starred current item."""

        user = info.context.user

        if user.is_anonymous:
            return False

        try:
            if isinstance(self, Course):
                # Ignore: pk attribute will be defined in the class deriving from this mixin.
                if user.stars.get(course=self.pk) is not None:  # type: ignore [attr-defined]
                    return True
                else:
                    return False
            if isinstance(self, Resource):
                # Ignore: pk attribute will be defined in the class deriving from this mixin.
                if user.stars.get(resource=self.pk) is not None:  # type: ignore [attr-defined]
                    return True
                else:
                    return False
            else:
                raise TypeError("Invalid class.")

        except Star.DoesNotExist:
            return False
