import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.schemas.school import SchoolType
from api.forms.resource import UploadResourceForm
from api.utils.points import get_points_for_target, POINTS_RESOURCE_MULTIPLIER
from api.utils.vote import AbstractUpvoteMutation, AbstractDownvoteMutation
from app.models import Resource, ResourceType as ResourceTypeModel, ResourcePart
from typing import Any, List
from mypy.types import JsonDict


class ResourcePartType(DjangoObjectType):
    class Meta:
        model = ResourcePart
        fields = ("id", "title", "file", "text", "file")


class ResourceTypeObjectType(DjangoObjectType):
    class Meta:
        model = ResourceTypeModel
        fields = ("id", "name", "has_parts")


class ResourceType(DjangoObjectType):
    resource_type = graphene.String()
    points = graphene.Int()
    school = graphene.Field(SchoolType)

    class Meta:
        model = Resource
        fields = ("id", "resource_parts", "title", "date", "course", "creator", "modified", "created")

    def resolve_points(self, info: ResolveInfo) -> int:
        return get_points_for_target(self, POINTS_RESOURCE_MULTIPLIER)

    def resolve_school(self, info: ResolveInfo) -> str:
        return self.course.school


class UpvoteResourceMutation(AbstractUpvoteMutation):
    class Input:
        resource_id = graphene.Int()

    resource = graphene.Field(ResourceType)


class DownvoteResourceMutation(AbstractDownvoteMutation):
    class Input:
        resource_id = graphene.Int()

    resource = graphene.Field(ResourceType)


class UploadResourceMutation(DjangoModelFormMutation):
    class Meta:
        form_class = UploadResourceForm

    @classmethod
    @login_required
    def perform_mutate(cls, form: UploadResourceForm, info: ResolveInfo) -> 'UploadResourceMutation':
        """Replace the form files with the actual files from the context. The resource manager
        will then take care of automatically creating resource parts based on the files.
        """

        form.cleaned_data.pop("files")
        resource = Resource.objects.create_resource(**form.cleaned_data, files=info.context.FILES)
        return cls(resource=resource)


class Query(graphene.ObjectType):
    resource = graphene.Field(ResourceType, resource_id=graphene.Int(required=True))
    resource_types = graphene.List(ResourceTypeObjectType)

    def resolve_resource(self, info: ResolveInfo, resource_id: str) -> Resource:
        try:
            return Resource.objects.get(pk=resource_id)
        except Resource.DoesNotExist:
            """Return 'None' instead of throwing a GraphQL Error."""
            return None

    def resolve_resource_types(self, info: ResolveInfo) -> List[ResourceTypeModel]:
        return ResourceTypeModel.objects.all()


class Mutation(graphene.ObjectType):
    upvote_resource = UpvoteResourceMutation.Field()
    downvote_resource = DownvoteResourceMutation.Field()
    upload_resource = UploadResourceMutation.Field()
