from typing import Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.resource import CreateUpdateResourceForm, DeleteResourceForm
from api.schemas.school import SchoolObjectType
from api.schemas.vote import VoteObjectType
from api.utils.common import get_obj_or_none
from api.utils.messages import NOT_OWNER_MESSAGE
from api.utils.mixins import DeleteMutationMixin
from api.utils.points import get_points_for_target
from core.models import Resource, Vote


class ResourceObjectType(DjangoObjectType):
    resource_type = graphene.String()
    points = graphene.Int()
    school = graphene.Field(SchoolObjectType)
    vote = graphene.Field(VoteObjectType)

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
        )

    def resolve_file(self, info: ResolveInfo) -> str:
        return f"media/{self.file}" if self.file else ""

    def resolve_points(self, info: ResolveInfo) -> int:
        return get_points_for_target(self)

    def resolve_school(self, info: ResolveInfo) -> str:
        return self.course.school

    def resolve_vote(self, info: ResolveInfo) -> Optional[int]:
        """Resolve current user's vote if it exists."""

        user = info.context.user

        if user.is_anonymous:
            return None

        try:
            return user.votes.get(comment=self.pk)
        except Vote.DoesNotExist:
            return None


class CreateResourceMutation(DjangoModelFormMutation):
    class Meta:
        form_class = CreateUpdateResourceForm
        exclude_fields = ("id",)

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: CreateUpdateResourceForm, info: ResolveInfo
    ) -> "CreateResourceMutation":
        """Replace the form files with the actual files from the context. The resource manager
        will then take care of automatically creating resource parts based on the files.
        """
        form.cleaned_data.pop("file")
        file = info.context.FILES.get("1")
        resource = Resource.objects.create_resource(
            **form.cleaned_data, file=file, user=info.context.user  # type: ignore
        )
        return cls(resource=resource)


class UpdateResourceMutation(DjangoModelFormMutation):
    class Meta:
        form_class = CreateUpdateResourceForm
        exclude_fields = ("course",)

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: CreateUpdateResourceForm, info: ResolveInfo
    ) -> "UpdateResourceMutation":

        try:
            resource = Resource.objects.get(pk=form.cleaned_data.pop("resource_id"))
        except Resource.DoesNotExist as e:
            # Camel case on purpose.
            return cls(errors=[{"field": "resourceId", "messages": [str(e)]}])

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
