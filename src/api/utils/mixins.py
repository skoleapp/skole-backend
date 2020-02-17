from typing import Any, Dict

import graphene
from django.utils.translation import gettext as _
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required
from api.utils.forms import DeleteObjectForm


class DeleteMutationMixin:
    """A base class for all delete mutations."""

    message = graphene.String()

    class Meta:
        return_field_name = "message"
        only_fields = ("id",)

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: Dict[str, Any]
    ) -> Dict[str, Any]:
        kwargs = {"data": input}
        pk = input.pop("id", None)

        if pk:
            instance = cls._meta.model._default_manager.get(pk=pk)  # type: ignore [attr-defined]
            kwargs["instance"] = instance
            kwargs["user"] = info.context.user

        return kwargs

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: DeleteObjectForm, info: ResolveInfo
    ) -> "DeleteMutationMixin":
        obj = form.cleaned_data.get("target")
        obj.delete()
        return cls(message=_("Object deleted successfully!"))  # type: ignore [call-arg]
