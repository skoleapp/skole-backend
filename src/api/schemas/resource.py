from typing import Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.resource import UpdateResourceForm, CreateResourceForm
from api.schemas.school import SchoolObjectType
from api.utils.common import get_obj_or_none
from api.utils.messages import NOT_OWNER_MESSAGE
from api.utils.points import POINTS_RESOURCE_MULTIPLIER, get_points_for_target
from app.models import Resource


class ResourceObjectType(DjangoObjectType):
    id = graphene.Int()
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


class CreateResourceMutation(DjangoModelFormMutation):
    class Meta:
        form_class = CreateResourceForm
        exclude_fields = ("id",)

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: CreateResourceForm, info: ResolveInfo
    ) -> "CreateResourceMutation":
        """Replace the form files with the actual files from the context. The resource manager
        will then take care of automatically creating resource parts based on the files.
        """

        form.cleaned_data.pop("files")
        resource = Resource.objects.create_resource(
            **form.cleaned_data, files=info.context.FILES, user=info.context.user  # type: ignore
        )
        return cls(resource=resource)


class UpdateResourceMutation(DjangoModelFormMutation):
    class Meta:
        form_class = UpdateResourceForm
        exclude_fields = ("id",)

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: UpdateResourceForm, info: ResolveInfo
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


class Query(graphene.ObjectType):
    resource = graphene.Field(
        ResourceObjectType, resource_id=graphene.Int(required=True)
    )

    def resolve_resource(
        self, info: ResolveInfo, resource_id: int
    ) -> Optional[Resource]:
        return get_obj_or_none(Resource, resource_id)


class Mutation(graphene.ObjectType):
    upload_resource = CreateResourceMutation.Field()
    update_resource = UpdateResourceMutation.Field()
