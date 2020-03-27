import graphene
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.starred import StarForm
from core.models.starred import Starred


class StarredMutation(DjangoModelFormMutation):
    starred = graphene.Boolean()

    class Meta:
        form_class = StarForm
        exclude_fields = ("id",)

    @classmethod
    @login_required
    def perform_mutate(cls, form: StarForm, info: ResolveInfo) -> "StarredMutation":
        starred = Starred.objects.perform_star(
            user=info.context.user, **form.cleaned_data
        )

        if starred is not None:
            # Ignore: value must be cast to boolean from Starred object.
            starred = True  # type: ignore [assignment]
        else:
            # Ignore: Same as above.
            starred = False  # type: ignore [assignment]

        return cls(starred=starred)


class Mutation(graphene.ObjectType):
    perform_star = StarredMutation.Field()
