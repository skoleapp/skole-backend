from typing import Literal, Optional

import graphene
from django.conf import settings
from django.db.models import Q, QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import CreateCommentForm, DeleteCommentForm, UpdateCommentForm
from skole.models import Comment, User
from skole.overridden import verification_required
from skole.schemas.base import (
    SkoleCreateUpdateMutationMixin,
    SkoleDeleteMutationMixin,
    SkoleObjectType,
)
from skole.schemas.mixins import PaginationMixin, SuccessMessageMixin, VoteMixin
from skole.types import ID, ResolveInfo
from skole.utils.constants import Messages
from skole.utils.pagination import get_paginator


class CommentObjectType(VoteMixin, DjangoObjectType):
    reply_count = graphene.Int()
    image_thumbnail = graphene.String()
    is_own = graphene.NonNull(graphene.Boolean)

    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "image",
            "image_thumbnail",
            "file",
            "score",
            "reply_count",
            "is_own",
            "created",
            "modified",
            "user",
            "thread",
            "vote",
            "reply_comments",
            "comment",
        )

    @staticmethod
    def resolve_user(root: Comment, info: ResolveInfo) -> Optional[User]:
        return root.user if not root.is_anonymous else None

    @staticmethod
    def resolve_is_own(root: Comment, info: ResolveInfo) -> bool:
        """
        Indicate which comments are owned by the current user.

        If comment is an own comment, the current user is also given options to for
        example delete it in the frontend.
        """

        return root.user == info.context.user

    @staticmethod
    def resolve_file(root: Comment, info: ResolveInfo) -> str:
        return root.file.url if root.file else ""

    @staticmethod
    def resolve_image(root: Comment, info: ResolveInfo) -> str:
        return root.image.url if root.image else ""

    @staticmethod
    def resolve_image_thumbnail(root: Comment, info: ResolveInfo) -> str:
        return root.image_thumbnail.url if root.image_thumbnail else ""

    @staticmethod
    def resolve_reply_count(root: Comment, info: ResolveInfo) -> int:
        # When the Comment is created and returned from a ModelForm it will not have
        # this field computed (it gets annotated only in the model manager) since the
        # value of this would be obviously 0 at the time of the comment's creation,
        # it's ok to return it as the default here.
        return getattr(root, "reply_count", 0)


class PaginatedCommentObjectType(PaginationMixin, SkoleObjectType):
    objects = graphene.List(CommentObjectType)

    class Meta:
        description = Comment.__doc__


class CreateCommentMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """
    Create a new comment.

    Attachments are popped of for unauthenticated users. The `user` field must match
    with the ID of the user making the query to save the user making the query as the
    author of the comment. This way even authenticated users can create anonymous
    comments by setting the `user` field as `null`.
    """

    verification_required = True
    success_message_value = Messages.MESSAGE_SENT

    class Meta:
        form_class = CreateCommentForm
        exclude_fields = ("id",)  # Without this, graphene adds the field on its own.


class UpdateCommentMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """Update an existing comment."""

    verification_required = True
    success_message_value = Messages.COMMENT_UPDATED

    comment = graphene.Field(CommentObjectType)

    class Meta:
        form_class = UpdateCommentForm


class DeleteCommentMutation(SkoleDeleteMutationMixin, DjangoModelFormMutation):
    """Delete a comment."""

    verification_required = True
    success_message_value = Messages.COMMENT_DELETED

    class Meta(SkoleDeleteMutationMixin.Meta):
        form_class = DeleteCommentForm


class Query(SkoleObjectType):
    comments = graphene.Field(
        PaginatedCommentObjectType,
        user=graphene.String(),
        thread=graphene.String(),
        comment=graphene.ID(),
        ordering=graphene.String(),
        page=graphene.Int(),
        page_size=graphene.Int(),
    )

    @staticmethod
    @verification_required
    def resolve_comments(
        root: None,
        info: ResolveInfo,
        user: str = "",
        thread: ID = "",
        comment: str = "",
        ordering: Literal["best", "newest"] = "best",
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> PaginatedCommentObjectType:
        """
        Return comments filtered by query params.

        The `search_term` is used to search from comment creator usernames and comment text.

        Results are sorted by creation time.
        """

        qs: QuerySet[Comment] = Comment.objects.all()

        if user != "":
            qs = qs.filter(user__slug=user)

        if thread != "":
            qs = qs.filter(thread__slug=thread)

        # Get a top comment that matches the query or one of its reply comments matches the query.
        # This way, the entire reply thread will be shown if a comment is provided as a parameter.
        if comment != "":
            qs = qs.filter(Q(pk=comment) | Q(reply_comments__pk=comment))

        if ordering == "best":
            qs = qs.order_by("-score")

        elif ordering == "newest":
            qs = qs.order_by("-pk")

        return get_paginator(qs, page_size, page, PaginatedCommentObjectType)


class Mutation(SkoleObjectType):
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()
