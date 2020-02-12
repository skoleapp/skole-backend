import graphene
from django.utils.translation import gettext as _
from graphene_django.forms.mutation import DjangoFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.delete import DeleteObjectForm


# FIXME: This mutation currently returns all form fields (that are always null) but we only want to return the message.
class DeleteObjectMutation(DjangoFormMutation):
    message = graphene.String()

    class Meta:
        form_class = DeleteObjectForm

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: DeleteObjectForm, info: ResolveInfo
    ) -> "DeleteObjectMutation":
        obj = form.cleaned_data.get("target")

        if obj.user != info.context.user:
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        "messages": [_("You are not the owner of this object!")],
                    }
                ]
            )

        obj.delete()
        return cls(message=_("Object deleted successfully!"))


class Mutation(graphene.ObjectType):
    delete_object = DeleteObjectMutation.Field()
