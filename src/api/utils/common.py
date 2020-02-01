from typing import Dict, Optional, Type

from django.db import models
from graphene.types.mutation import MutationOptions


def get_obj_or_none(model: Type[models.Model], obj_id: int) -> Optional[models.Model]:
    """Used as a helper function to return None instead of raising
    a GraphQLError."""
    try:
        return model.objects.get(pk=obj_id)
    except model.DoesNotExist:
        return None


def get_object_from_meta_and_kwargs(
    meta: MutationOptions, kwargs_of_caller: Dict[str, int]
) -> models.Model:
    """Return the Model instance which we are mutating from a graphene.Mutation."""
    if len(meta.fields) != 1 or len(meta.arguments) != 1 or len(kwargs_of_caller) != 1:
        # FIXME: this bleeds straight into graphql's error messages
        #  it apparently catches every single exception and puts the
        #  message of the error as the message in the graphql response.
        raise AssertionError(
            "Expected derived mutation to have exactly one graphene field and taking exactly one argument."
        )

    # Get the model we are mutating. e.g. Course
    # Since we only have one field, this just accesses it.
    model = list(meta.fields.values())[0]._type._meta.model

    _, obj_id = kwargs_of_caller.popitem()

    return model.objects.get(pk=obj_id)
