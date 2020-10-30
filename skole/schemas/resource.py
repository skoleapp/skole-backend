from typing import Optional

import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql_jwt.decorators import login_required

from skole.forms import CreateResourceForm, DeleteResourceForm, UpdateResourceForm
from skole.models import Resource, School
from skole.schemas.mixins import (
    PaginationMixin,
    SkoleCreateUpdateMutationMixin,
    SkoleDeleteMutationMixin,
    StarMixin,
    SuccessMessageMixin,
    VoteMixin,
)
from skole.schemas.resource_type import ResourceTypeObjectType
from skole.schemas.school import SchoolObjectType
from skole.types import ID, ResolveInfo
from skole.utils.api_descriptions import APIDescriptions
from skole.utils.constants import Messages
from skole.utils.pagination import get_paginator


class ResourceObjectType(VoteMixin, StarMixin, DjangoObjectType):
    resource_type = graphene.Field(ResourceTypeObjectType)
    school = graphene.Field(SchoolObjectType)
    star_count = graphene.Int()
    comment_count = graphene.Int()

    class Meta:
        model = Resource
        description = APIDescriptions.RESOURCE_OBJECT_TYPE
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
            "score",
            "star_count",
            "comment_count",
        )

    @staticmethod
    def resolve_file(root: Resource, info: ResolveInfo) -> str:
        return root.file.url if root.file else ""

    @staticmethod
    def resolve_school(root: Resource, info: ResolveInfo) -> School:
        return root.course.school

    # Have to specify these with resolvers since graphene cannot infer the annotated fields otherwise.

    @staticmethod
    def resolve_star_count(root: Resource, info: ResolveInfo) -> int:
        return getattr(root, "star_count", 0)

    @staticmethod
    def resolve_comment_count(root: Resource, info: ResolveInfo) -> int:
        # When the Resource is created and returned from a ModelForm it will not have
        # this field computed (it gets annotated only in the model manager) since the
        # value of this would be obviously 0 at the time of the resource's creation,
        # it's ok to return it as the default here.
        return getattr(root, "comment_count", 0)


class PaginatedResourceObjectType(PaginationMixin, graphene.ObjectType):
    objects = graphene.List(ResourceObjectType)


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
    verification_required = True
    success_message = Messages.RESOURCE_DELETED

    class Meta(SkoleDeleteMutationMixin.Meta):
        form_class = DeleteResourceForm


class Query(graphene.ObjectType):
    resources = graphene.Field(
        PaginatedResourceObjectType,
        course=graphene.ID(),
        description=APIDescriptions.RESOURCES,
    )

    created_resources = graphene.Field(
        PaginatedResourceObjectType,
        user=graphene.ID(),
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
        description=APIDescriptions.CREATED_RESOURCES,
    )

    starred_resources = graphene.Field(
        PaginatedResourceObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
        description=APIDescriptions.STARRED_RESOURCES,
    )

    resource = graphene.Field(
        ResourceObjectType, id=graphene.ID(), description=APIDescriptions.RESOURCE,
    )

    @staticmethod
    def resolve_resources(
        root: None,
        info: ResolveInfo,
        page: int = 1,
        course: ID = None,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> graphene.ObjectType:
        if course is not None:
            qs = Resource.objects.filter(course__pk=course)
        else:
            qs = Resource.objects.none()

        return get_paginator(qs, page_size, page, PaginatedResourceObjectType)

    @staticmethod
    def resolve_created_resources(
        root: None,
        info: ResolveInfo,
        user: ID = None,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> graphene.ObjectType:
        if user is not None:
            user_from_db = get_user_model().objects.get_or_none(pk=user)
        else:
            user_from_db = None

        if user_from_db is not None:
            qs: QuerySet[Resource] = user_from_db.created_resources.all()
        else:
            # The user with the provided ID does not exist, we return an empty list.
            qs = Resource.objects.none()

        return get_paginator(qs, page_size, page, PaginatedResourceObjectType)

    @staticmethod
    @login_required
    def resolve_starred_resources(
        root: None,
        info: ResolveInfo,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> QuerySet[Resource]:
        qs = Resource.objects.filter(stars__user__pk=info.context.user.pk)
        return get_paginator(qs, page_size, page, PaginatedResourceObjectType)

    @staticmethod
    def resolve_resource(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[Resource]:
        return Resource.objects.get_or_none(pk=id)


class Mutation(graphene.ObjectType):
    create_resource = CreateResourceMutation.Field(
        description=APIDescriptions.CREATE_RESOURCE
    )

    update_resource = UpdateResourceMutation.Field(
        description=APIDescriptions.UPDATE_RESOURCE
    )

    delete_resource = DeleteResourceMutation.Field(
        description=APIDescriptions.DELETE_RESOURCE
    )
