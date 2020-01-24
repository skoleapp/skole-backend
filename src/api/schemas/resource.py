from typing import Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.resource import UploadResourceForm
from api.schemas.school import SchoolObjectType
from api.utils.points import POINTS_RESOURCE_MULTIPLIER, get_points_for_target
from api.utils.vote import AbstractDownvoteMutation, AbstractUpvoteMutation
from app.models import Resource


class ResourceObjectType(DjangoObjectType):
    resource_type = graphene.String()
    points = graphene.Int()
    school = graphene.Field(SchoolObjectType)

    class Meta:
        model = Resource
        fields = (
            "id",
            "resource_parts",
            "title",
            "date",
            "course",
            "downloads",
            "user",
            "modified",
            "created",
            "comments",
        )

    def resolve_points(self, info: ResolveInfo) -> int:
        return get_points_for_target(self, POINTS_RESOURCE_MULTIPLIER)

    def resolve_school(self, info: ResolveInfo) -> str:
        return self.course.school


class UpvoteResourceMutation(AbstractUpvoteMutation):
    class Arguments:
        resource_id = graphene.Int()

    resource = graphene.Field(ResourceObjectType)


class DownvoteResourceMutation(AbstractDownvoteMutation):
    class Arguments:
        resource_id = graphene.Int()

    resource = graphene.Field(ResourceObjectType)


class UploadResourceMutation(DjangoModelFormMutation):
    class Meta:
        form_class = UploadResourceForm

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: UploadResourceForm, info: ResolveInfo
    ) -> "UploadResourceMutation":
        """Replace the form files with the actual files from the context. The resource manager
        will then take care of automatically creating resource parts based on the files.
        """

        form.cleaned_data.pop("files")
        resource = Resource.objects.create_resource(
            **form.cleaned_data, files=info.context.FILES, user=info.context.user  # type: ignore
        )
        return cls(resource=resource)


class Query(graphene.ObjectType):
    resource = graphene.Field(
        ResourceObjectType, resource_id=graphene.Int(required=True)
    )

    def resolve_resource(
        self, info: ResolveInfo, resource_id: str
    ) -> Optional[Resource]:
        try:
            return Resource.objects.get(pk=resource_id)
        except Resource.DoesNotExist:
            # Return None instead of throwing a GraphQL Error.
            return None


class Mutation(graphene.ObjectType):
    upvote_resource = UpvoteResourceMutation.Field()
    downvote_resource = DownvoteResourceMutation.Field()
    upload_resource = UploadResourceMutation.Field()
