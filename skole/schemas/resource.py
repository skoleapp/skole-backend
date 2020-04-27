from typing import Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from skole.forms.resource import (CreateResourceForm, DeleteResourceForm,
                                  UpdateResourceForm)
from skole.models import Resource
from skole.schemas.school import SchoolObjectType
from skole.utils.constants import Messages, MutationErrors
from skole.utils.decorators import login_required_mutation
from skole.utils.mixins import (DeleteMutationMixin, FileMutationMixin,
                                MessageMixin, StarredMixin, VoteMixin)
from skole.utils.shortcuts import get_obj_or_none


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


class CreateResourceMutation(FileMutationMixin, MessageMixin, DjangoModelFormMutation):
    class Meta:
        form_class = CreateResourceForm
        exclude_fields = ("id",)

    @classmethod
    @login_required_mutation
    def perform_mutate(
        cls, form: CreateResourceForm, info: ResolveInfo
    ) -> "CreateResourceMutation":
        assert info.context is not None
        resource = Resource.objects.create_resource(
            #  Mypy somehow thinks that the user was already in the cleaned_data,
            #  and would thus also be a duplicate key.
            **form.cleaned_data, user=info.context.user # type: ignore[misc]
        )
        return cls(resource=resource, message=Messages.RESOURCE_CREATED)


class UpdateResourceMutation(MessageMixin, DjangoModelFormMutation):
    class Meta:
        form_class = UpdateResourceForm

    @classmethod
    @login_required_mutation
    def perform_mutate(
        cls, form: UpdateResourceForm, info: ResolveInfo
    ) -> "UpdateResourceMutation":
        assert info.context is not None
        resource = form.instance

        if resource.user != info.context.user:
            return cls(errors=MutationErrors.NOT_OWNER)

        Resource.objects.update_resource(resource, **form.cleaned_data)
        return cls(resource=resource, message=Messages.RESOURCE_UPDATED)


class DeleteResourceMutation(DeleteMutationMixin, DjangoModelFormMutation):
    class Meta(DeleteMutationMixin.Meta):
        form_class = DeleteResourceForm

    @staticmethod
    def get_success_message() -> str:
        return Messages.RESOURCE_DELETED


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
