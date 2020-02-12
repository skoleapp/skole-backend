import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.resource_part import CreateResourcePartForm, UpdateResourcePartForm
from app.models import ResourcePart


class ResourcePartObjectType(DjangoObjectType):
    class Meta:
        model = ResourcePart
        fields = ("id", "title", "file", "text", "file")

    def resolve_file(self, info: ResolveInfo) -> str:
        return f"media/{self.file}"


class CreateResourcePartMutation(DjangoModelFormMutation):
    class Meta:
        form_class = CreateResourcePartForm
        exclude_fields = ("id",)

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: CreateResourcePartForm, info: ResolveInfo
    ) -> "CreateResourcePartMutation":
        # Replace the form file with the actual file from the context.
        form.cleaned_data["file"] = list(info.context.FILES.values())[0]
        resource_part = ResourcePart.objects.create(**form.cleaned_data)
        return cls(resource_part=resource_part)


class UpdateResourcePartMutation(DjangoModelFormMutation):
    class Meta:
        form_class = UpdateResourcePartForm

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: UpdateResourcePartForm, info: ResolveInfo
    ) -> "UpdateResourcePartMutation":
        # Replace the form file with the actual file from the context.
        form.cleaned_data["file"] = list(info.context.FILES.values())[0]

        instance = ResourcePart.objects.get(
            pk=form.cleaned_data.pop("resource_part_id")
        )

        resource_part = ResourcePart.objects.update(
            instance=instance, **form.cleaned_data
        )

        return cls(resource_part=resource_part)


class Mutation(graphene.ObjectType):
    create_resource_part = CreateResourcePartMutation.Field()
    update_resource_part = UpdateResourcePartMutation.Field()
