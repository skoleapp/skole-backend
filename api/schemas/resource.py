from typing import Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.resource import CreateResourceForm, DeleteResourceForm, UpdateResourceForm
from api.schemas.school import SchoolObjectType
from api.utils.common import get_obj_or_none
from api.utils.delete import DeleteMutationMixin
from api.utils.file import FileMixin
from api.utils.messages import NOT_OWNER_MESSAGE
from api.utils.starred import StarredMixin
from api.utils.vote import VoteMixin
from core.models import Resource


class ResourceObjectType(VoteMixin, StarredMixin, DjangoObjectType):
    resource_type = graphene.String()
    school = graphene.Field(SchoolObjectType)

    class Meta:
        model = Resource
        fields = (
            "id",
            "file",
            "title",
            "date",
            "course",
            "downloads",
            "user",
            "modified",
            "created",
            "comments",
            "resource_type",
            "school",
        )

    def resolve_file(self, info: ResolveInfo) -> str:
        return self.file.url if self.file else ""

    def resolve_school(self, info: ResolveInfo) -> str:
        return self.course.school


class CreateResourceMutation(FileMixin, DjangoModelFormMutation):
    class Meta:
        form_class = CreateResourceForm
        exclude_fields = ("id",)

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: CreateResourceForm, info: ResolveInfo
    ) -> "CreateResourceMutation":
        assert info.context is not None
        resource = Resource.objects.create_resource(
            #  Mypy somehow thinks that the user was already in the cleaned_data,
            #  and would thus also be a duplicate key.
            **form.cleaned_data, user=info.context.user # type: ignore[misc]
        )
        return cls(resource=resource)


class UpdateResourceMutation(DjangoModelFormMutation):
    class Meta:
        form_class = UpdateResourceForm

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: UpdateResourceForm, info: ResolveInfo
    ) -> "UpdateResourceMutation":
        assert info.context is not None

        resource = form.instance
        if resource.user != info.context.user:
            return cls(errors=[{"field": "__all__", "messages": [NOT_OWNER_MESSAGE]}])

        Resource.objects.update_resource(resource, **form.cleaned_data)
        return cls(resource=resource)


class DeleteResourceMutation(DeleteMutationMixin, DjangoModelFormMutation):
    class Meta(DeleteMutationMixin.Meta):
        form_class = DeleteResourceForm


class Query(graphene.ObjectType):
    resource = graphene.Field(ResourceObjectType, id=graphene.ID())

    @login_required
    def resolve_resource(
        self, info: ResolveInfo, id: Optional[int] = None
    ) -> Optional[Resource]:
        return get_obj_or_none(Resource, id)


class Mutation(graphene.ObjectType):
    create_resource = CreateResourceMutation.Field()
    update_resource = UpdateResourceMutation.Field()
    delete_resource = DeleteResourceMutation.Field()
