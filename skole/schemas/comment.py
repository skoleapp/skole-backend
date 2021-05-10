from __future__ import annotations

from typing import Literal, Optional

import graphene
from django.conf import settings
from django.db.models import QuerySet
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
            "file_thumbnail",
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
    def resolve_file_thumbnail(root: Comment, info: ResolveInfo) -> str:
        return root.get_or_create_file_thumbnail_url()

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
        thread: str = "",
        comment: ID = None,
        ordering: Literal["best", "newest"] = "best",
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> PaginatedCommentObjectType:
        """
        Return comments filtered by query params.

        Either the `thread` or `user` argument must be passed, otherwise the results
        will be empty.

        If the `thread` is passed the results are sorted according to the `ordering`
        argument. If the `user` argument is passed the results will always
        just be sorted by creation time.
        """

        qs: QuerySet[Comment] = Comment.objects.all()

        if user != "":
            # Just show these chronologically when querying in a user profile.
            qs = qs.filter(user__slug=user, is_anonymous=False).order_by("-pk")
        elif thread != "":
            qs = qs.filter(thread__slug=thread)
            if ordering == "best":
                qs = qs.order_by("-score", "pk")
            elif ordering == "newest":
                qs = qs.order_by("-pk")
        else:
            qs = qs.none()

        paginated_qs = get_paginator(qs, page_size, page, PaginatedCommentObjectType)

        if comment_obj := Comment.objects.get_or_none(pk=comment):
            # If the comment is a reply comment, find it's top comment.
            if top_comment := comment_obj.comment:
                comment_obj = top_comment

            for page_num in range(0, paginated_qs.pages):
                temp_paginated_qs = get_paginator(
                    qs, page_size, page_num, PaginatedCommentObjectType
                )

                # If the comment exists on some of the pages of the paginated queryset, return the paginated results on that page.
                # Ignore: Pylint doesn't recognize the `objects`-attribute is a list.
                if (
                    comment_obj
                    in temp_paginated_qs.objects  # pylint: disable=unsupported-membership-test
                ):
                    return temp_paginated_qs

        return paginated_qs


class Mutation(SkoleObjectType):
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()
