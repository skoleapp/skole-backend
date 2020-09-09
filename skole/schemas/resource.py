from typing import Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo

from skole.forms import CreateResourceForm, DeleteResourceForm, UpdateResourceForm
from skole.models import Resource
from skole.schemas.mixins import (
    SkoleCreateUpdateMutationMixin,
    SkoleDeleteMutationMixin,
    StarredMixin,
    SuccessMessageMixin,
    VoteMixin,
)
from skole.schemas.school import SchoolObjectType
from skole.types import ID
from skole.utils.constants import Messages
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


class CreateResourceMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    verification_required = True
    success_message = Messages.RESOURCE_CREATED

    class Meta:
        form_class = CreateResourceForm
        exclude_fields = ("id",)


class UpdateResourceMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    verification_required = True
    success_message = Messages.RESOURCE_UPDATED

    class Meta:
        form_class = UpdateResourceForm


class DeleteResourceMutation(SkoleDeleteMutationMixin, DjangoModelFormMutation):
    success_message = Messages.RESOURCE_DELETED

    class Meta(SkoleDeleteMutationMixin.Meta):
        form_class = DeleteResourceForm


class Query(graphene.ObjectType):
    resource = graphene.Field(ResourceObjectType, id=graphene.ID())

    def resolve_resource(self, info: ResolveInfo, id: ID = None) -> Optional[Resource]:
        return get_obj_or_none(Resource, id)


class Mutation(graphene.ObjectType):
    create_resource = CreateResourceMutation.Field()
    update_resource = UpdateResourceMutation.Field()
    delete_resource = DeleteResourceMutation.Field()
