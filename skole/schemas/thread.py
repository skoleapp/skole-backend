from __future__ import annotations

from typing import Literal, Optional, cast

import graphene
from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, QuerySet
from django.db.models.functions import ExtractDay, Greatest
from django.utils import timezone
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import CreateThreadForm, DeleteThreadForm
from skole.models import Thread, User
from skole.overridden import verification_required
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
from skole.types import ResolveInfo
from skole.utils.constants import Messages
from skole.utils.pagination import get_paginator


def order_threads_with_secret_algorithm(qs: QuerySet[Thread]) -> QuerySet[Thread]:
    """
    Sort the given queryset so that the most interesting threads come first.

    No deep logic in this, should just be a formula that makes the most sense for
    determining the most interesting threads.

    The ordering formula/value should not be exposed to the frontend.
    """

    # Ignore: Mypy thinks this is faulty but it works fine.
    today = timezone.now().date()
    return qs.order_by(
        -(
            3 * F("score")
            + 2 * F("comment_count")
            - ExtractDay(today - F("created__date")) / 2  # type: ignore[operator]
        ),
        "pk",
    )


class ThreadObjectType(VoteMixin, StarMixin, DjangoObjectType):
    star_count = graphene.Int()
    comment_count = graphene.Int()
    image_thumbnail = graphene.String()

    class Meta:
        model = Thread
        fields = (
            "id",
            "slug",
            "title",
            "text",
            "image",
            "image_thumbnail",
            "score",
            "starred",
            "star_count",
            "comment_count",
            "created",
            "modified",
            "vote",
            "user",
            "views",
        )

    @staticmethod
    def resolve_image(root: Thread, info: ResolveInfo) -> str:
        return root.image.url if root.image else ""

    @staticmethod
    def resolve_image_thumbnail(root: Thread, info: ResolveInfo) -> str:
        return root.image_thumbnail.url if root.image_thumbnail else ""

    # Have to specify these with resolvers since graphene
    # cannot infer the annotated fields otherwise.

    @staticmethod
    def resolve_star_count(root: Thread, info: ResolveInfo) -> int:
        return getattr(root, "star_count", 0)

    @staticmethod
    def resolve_comment_count(root: Thread, info: ResolveInfo) -> int:
        # When the Thread is created and returned from a ModelForm it will not have
        # this field computed (it gets annotated only in the model manager) since the
        # value of this would be obviously 0 at the time of the thread's creation,
        # it's ok to return it as the default here.
        return getattr(root, "comment_count", 0)


class PaginatedThreadObjectType(PaginationMixin, SkoleObjectType):
    objects = graphene.List(ThreadObjectType)

    class Meta:
        description = Thread.__doc__


class CreateThreadMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """Create a new thread."""

    verification_required = True
    success_message_value = Messages.THREAD_CREATED
    thread = graphene.Field(ThreadObjectType)

    class Meta:
        form_class = CreateThreadForm
        exclude_fields = ("id",)


class DeleteThreadMutation(SkoleDeleteMutationMixin, DjangoModelFormMutation):
    """Delete a thread."""

    verification_required = True
    success_message_value = Messages.THREAD_DELETED

    class Meta(SkoleDeleteMutationMixin.Meta):
        form_class = DeleteThreadForm


class Query(SkoleObjectType):
    threads = graphene.Field(
        PaginatedThreadObjectType,
        search_term=graphene.String(),
        user=graphene.String(),
        ordering=graphene.String(),
        page=graphene.Int(),
        page_size=graphene.Int(),
    )

    starred_threads = graphene.Field(
        PaginatedThreadObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
    )

    thread = graphene.Field(ThreadObjectType, slug=graphene.String())

    @staticmethod
    @verification_required
    def resolve_threads(
        root: None,
        info: ResolveInfo,
        search_term: str = "",
        user: str = "",
        ordering: Literal["best", "newest"] = "best",
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> PaginatedThreadObjectType:
        """
        Return threads filtered by query params.

        The `search_term` is used to search from thread title and text.

        Results are sorted either manually based on query params or by secret Skole AI-
        powered algorithms. If the `user` argument is passed the results will always
        just be sorted by creation time.
        """

        qs: QuerySet[Thread] = Thread.objects.all()

        if user != "":
            # Just show these chronologically when querying in a user profile.
            qs = qs.filter(user__slug=user).order_by("-pk")
        elif search_term != "":
            qs = (
                qs.annotate(
                    similarity=Greatest(
                        TrigramSimilarity("title", search_term),
                        TrigramSimilarity("text", search_term),
                    )
                )
                # Tested that this works quite well as a threshold here.
                .filter(similarity__gte=0.1).order_by("-similarity", "pk")
            )
        elif ordering == "newest":
            qs = qs.order_by("-pk")
        else:  # "best"
            qs = order_threads_with_secret_algorithm(qs)

        return get_paginator(qs, page_size, page, PaginatedThreadObjectType)

    @staticmethod
    @verification_required
    def resolve_starred_threads(
        root: None,
        info: ResolveInfo,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> PaginatedThreadObjectType:
        """
        Return starred threads of the user making the query.

        Results are sorted by creation time. Return an empty list for unauthenticated
        users.
        """

        user = cast(User, info.context.user)
        qs = Thread.objects.filter(stars__user=user)
        qs = qs.order_by("pk")
        return get_paginator(qs, page_size, page, PaginatedThreadObjectType)

    @staticmethod
    def resolve_thread(
        root: None, info: ResolveInfo, slug: str = ""
    ) -> Optional[Thread]:
        try:
            thread = Thread.objects.get(slug=slug)
            thread.increment_views(info.context)
            return thread
        except Thread.DoesNotExist:
            return None


class Mutation(SkoleObjectType):
    create_thread = CreateThreadMutation.Field()
    delete_thread = DeleteThreadMutation.Field()
