from typing import Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo

from skole.forms import CreateResourceForm, DeleteResourceForm, UpdateResourceForm
from skole.models import Resource, School
from skole.schemas.mixins import (
    SkoleCreateUpdateMutationMixin,
    SkoleDeleteMutationMixin,
    StarredMixin,
    SuccessMessageMixin,
    VoteMixin,
)
from skole.schemas.resource_type import ResourceTypeObjectType
from skole.schemas.school import SchoolObjectType
from skole.types import ID
from skole.utils.constants import Messages


class ResourceObjectType(VoteMixin, StarredMixin, DjangoObjectType):
    resource_type = graphene.Field(ResourceTypeObjectType)
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

    @staticmethod
    def resolve_file(root: Resource, info: ResolveInfo) -> str:
        return root.file.url if root.file else ""

    @staticmethod
    def resolve_school(root: Resource, info: ResolveInfo) -> School:
        return root.course.school


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

    @staticmethod
    def resolve_resource(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[Resource]:
        return Resource.objects.get_or_none(pk=id)


class Mutation(graphene.ObjectType):
    create_resource = CreateResourceMutation.Field()
    update_resource = UpdateResourceMutation.Field()
    delete_resource = DeleteResourceMutation.Field()
