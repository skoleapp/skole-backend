from typing import Optional

import graphene
from django.conf import settings
from django.db.models import F, QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import (
    CreateResourceForm,
    DeleteResourceForm,
    DownloadResourceForm,
    UpdateResourceForm,
)
from skole.models import Resource, School
from skole.overridden import login_required
from skole.schemas.author import AuthorObjectType
from skole.schemas.base import (
    SkoleCreateUpdateMutationMixin,
    SkoleDeleteMutationMixin,
    SkoleObjectType,
)
from skole.schemas.mixins import (
    PaginationMixin,
    StarMixin,
    SuccessMessageMixin,
    VoteMixin,
)
from skole.schemas.resource_type import ResourceTypeObjectType
from skole.schemas.school import SchoolObjectType
from skole.schemas.course import CourseObjectType
from skole.types import ID, ResolveInfo
from skole.utils.constants import Messages
from skole.utils.pagination import get_paginator


def order_resources_with_secret_algorithm(qs: QuerySet[Resource]) -> QuerySet[Resource]:
    """
    Sort the given queryset so that the most interesting resources come first.

    No deep logic in this, should just be a formula that makes the most sense for
    determining the most interesting resources.

    The ordering formula/value should not be exposed to the frontend.
    """

    return qs.order_by(-(3 * F("score") + F("comment_count") + F("downloads")), "title")


class ResourceObjectType(VoteMixin, StarMixin, DjangoObjectType):
    resource_type = graphene.Field(ResourceTypeObjectType)
    school = graphene.Field(SchoolObjectType)
    course = graphene.Field(CourseObjectType)
    author = graphene.Field(AuthorObjectType)
    star_count = graphene.Int()
    comment_count = graphene.Int()

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
            "author",
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


class PaginatedResourceObjectType(PaginationMixin, SkoleObjectType):
    objects = graphene.List(ResourceObjectType)

    class Meta:
        description = Resource.__doc__


class CreateResourceMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """Create a new resource."""

    verification_required = True
    success_message_value = Messages.RESOURCE_CREATED

    class Meta:
        form_class = CreateResourceForm
        exclude_fields = ("id",)


class UpdateResourceMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """Update a resource."""

    verification_required = True
    success_message_value = Messages.RESOURCE_UPDATED

    class Meta:
        form_class = UpdateResourceForm


class DeleteResourceMutation(SkoleDeleteMutationMixin, DjangoModelFormMutation):
    """
    Delete a resource.

    Results are sorted by creation time.
    """

    verification_required = True
    success_message_value = Messages.RESOURCE_DELETED

    class Meta(SkoleDeleteMutationMixin.Meta):
        form_class = DeleteResourceForm


class DownloadResourceMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """
    Download a resource.

    This mutation only increments the amount of downloads of a single resource.
    """

    success_message_value = Messages.RESOURCE_DOWNLOADS_UPDATED

    class Meta:
        form_class = DownloadResourceForm


class Query(SkoleObjectType):
    resources = graphene.Field(
        PaginatedResourceObjectType,
        user=graphene.ID(),
        course=graphene.ID(),
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
    )

    starred_resources = graphene.Field(
        PaginatedResourceObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
    )

    resource = graphene.Field(ResourceObjectType, id=graphene.ID())

    @staticmethod
    def resolve_resources(
        root: None,
        info: ResolveInfo,
        user: ID = None,
        course: ID = None,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> PaginatedResourceObjectType:
        """
        Return resources filtered by query params.

        Results are sorted by creation time.
        """
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
    ) -> PaginatedResourceObjectType:
        """
        Return starred resources of the user making the query.

        Results are sorted by creation time.
        """
        qs = Resource.objects.filter(stars__user__pk=info.context.user.pk)
        qs = qs.order_by("pk")
        return get_paginator(qs, page_size, page, PaginatedResourceObjectType)

    @staticmethod
    def resolve_resource(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[Resource]:
        return Resource.objects.get_or_none(pk=id)


class Mutation(SkoleObjectType):
    create_resource = CreateResourceMutation.Field()
    update_resource = UpdateResourceMutation.Field()
    delete_resource = DeleteResourceMutation.Field()
    download_resource = DownloadResourceMutation.Field()
