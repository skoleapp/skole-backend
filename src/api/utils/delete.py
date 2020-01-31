from typing import Any

import graphene
from graphql import GraphQLError, ResolveInfo
from graphql_jwt.decorators import login_required

from api.utils.common import get_object_from_meta_and_kwargs
from api.utils.messages import NOT_ALLOWED_TO_MUTATE_MESSAGE


class AbstractDeleteMutation(graphene.Mutation):
    """Base class for all delete mutations. This can be subclassed in any schema
    that needs the ability to delete a model with a mutation.
    """

    @classmethod
    @login_required
    def mutate(
        cls, root: Any, info: ResolveInfo, **kwargs: int
    ) -> "AbstractDeleteMutation":
        obj = get_object_from_meta_and_kwargs(cls._meta, kwargs)

        if hasattr(obj, "user") and obj.user != info.context.user:
            raise GraphQLError(NOT_ALLOWED_TO_MUTATE_MESSAGE)

        obj.delete()
        # Now returns;
        # {
        #   "data": {
        #     "deleteResource": {
        #       "resource": null
        #     }
        #   }
        # }
        # Should this instead return some kind of message, like deleting a User does.
        return cls()
