from typing import Optional

import graphene
from django.conf import settings
from django.db.models import F, QuerySet
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
from skole.utils import api_descriptions
from skole.utils.constants import Messages
from skole.utils.pagination import get_paginator


def order_resources_with_secret_algorithm(qs: QuerySet[Resource]) -> QuerySet[Resource]:
    """
    Sort the given queryset so that the most interesting resources come first.

    No deep logic in this, should just be a formula that makes the most sense for
    determining the most interesting resources.

    The ordering formula/value should not be exposed to the frontend.
    """

    return qs.order_by(-(3 * F("score") + F("comment_count")), "title")


class ResourceObjectType(VoteMixin, StarMixin, DjangoObjectType):
    resource_type = graphene.Field(ResourceTypeObjectType)
    school = graphene.Field(SchoolObjectType)
    star_count = graphene.Int()
    comment_count = graphene.Int()

    class Meta:
        model = Resource
        description = api_descriptions.RESOURCE_OBJECT_TYPE
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
        user=graphene.ID(),
        course=graphene.ID(),
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
        description=api_descriptions.RESOURCES,
    )

    starred_resources = graphene.Field(
        PaginatedResourceObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
        description=api_descriptions.STARRED_RESOURCES,
    )

    resource = graphene.Field(
        ResourceObjectType, id=graphene.ID(), description=api_descriptions.RESOURCE,
    )

    @staticmethod
    def resolve_resources(
        root: None,
        info: ResolveInfo,
        user: ID = None,
        course: ID = None,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> graphene.ObjectType:
        qs: QuerySet[Resource] = Resource.objects.all()

        if user is not None:
            qs = qs.filter(user__pk=user)
        if course is not None:
            qs = qs.filter(course__pk=course)

        qs = order_resources_with_secret_algorithm(qs)
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
        description=api_descriptions.CREATE_RESOURCE
    )

    update_resource = UpdateResourceMutation.Field(
        description=api_descriptions.UPDATE_RESOURCE
    )

    delete_resource = DeleteResourceMutation.Field(
        description=api_descriptions.DELETE_RESOURCE
    )
