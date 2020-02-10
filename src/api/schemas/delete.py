import graphene
from django.utils.translation import gettext as _
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.delete import DeleteObjectForm


class DeleteObjectMutation(DjangoModelFormMutation):
    message = graphene.String()

    class Meta:
        form_class = DeleteObjectForm
        exclude_fields = ("id",)
        return_field_name = "message"

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: DeleteObjectForm, info: ResolveInfo
    ) -> "DeleteObjectMutation":
        obj = form.cleaned_data.get("target")
        obj.delete()
        return cls(message=_("Object deleted successfully!"))


class Mutation(graphene.ObjectType):
    delete_object = DeleteObjectMutation.Field()
