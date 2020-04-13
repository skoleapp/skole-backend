import graphene
from graphql import ResolveInfo

from core.models import Starred


class StarredMixin:
    starred = graphene.Boolean()

    def resolve_starred(self, info: ResolveInfo) -> bool:
        """Check whether user has starred the current item."""
        assert info.context is not None

        user = info.context.user

        if user.is_anonymous:
            return False

        try:
            # Ignore: pk attribute will be defined in the class deriving from this mixin.
            return user.stars.get(**{self.__class__.__name__.lower(): self.pk}) is not None  # type: ignore [attr-defined]
        except Starred.DoesNotExist:
            return False
