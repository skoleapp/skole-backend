import graphene
from django.conf import settings
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import CreateCommentForm, DeleteCommentForm, UpdateCommentForm
from skole.models import Comment
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
    attachment_thumbnail = graphene.String()

    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "text",
            "attachment",
            "attachment_thumbnail",
            "course",
            "resource",
            "comment",
            "reply_comments",
            "reply_count",
            "score",
            "modified",
            "created",
        )

    @staticmethod
    def resolve_attachment(root: Comment, info: ResolveInfo) -> str:
        return root.attachment.url if root.attachment else ""

    @staticmethod
    def resolve_attachment_thumbnail(root: Comment, info: ResolveInfo) -> str:
        return root.attachment_thumbnail.url if root.attachment_thumbnail else ""

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

    success_message_value = Messages.MESSAGE_SENT

    class Meta:
        form_class = CreateCommentForm
        exclude_fields = ("id",)  # Without this, graphene adds the field on its own.


class UpdateCommentMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """Update an existing comment."""

    login_required = True
    success_message_value = Messages.COMMENT_UPDATED
    comment = graphene.Field(CommentObjectType)

    class Meta:
        form_class = UpdateCommentForm


class DeleteCommentMutation(SkoleDeleteMutationMixin, DjangoModelFormMutation):
    """Delete a comment."""

    success_message_value = Messages.COMMENT_DELETED

    class Meta(SkoleDeleteMutationMixin.Meta):
        form_class = DeleteCommentForm


class Query(SkoleObjectType):
    comments = graphene.Field(
        PaginatedCommentObjectType,
        user=graphene.ID(),
        page=graphene.Int(),
        page_size=graphene.Int(),
    )

    discussion = graphene.List(
        CommentObjectType,
        course=graphene.ID(),
        resource=graphene.ID(),
    )

    @staticmethod
    def resolve_comments(
        root: None,
        info: ResolveInfo,
        user: ID = None,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> PaginatedCommentObjectType:
        """Return comments filtered by query params."""

        qs: QuerySet[Comment] = Comment.objects.all()

        if user is not None:
            qs = qs.filter(user__pk=user)

        return get_paginator(qs, page_size, page, PaginatedCommentObjectType)

    @staticmethod
    def resolve_discussion(
        root: None,
        info: ResolveInfo,
        course: ID = None,
        resource: ID = None,
    ) -> QuerySet[Comment]:
        """Return comments filtered by query params."""

        qs = Comment.objects.all()

        if course is not None:
            qs = qs.filter(course__pk=course)
        if resource is not None:
            qs = qs.filter(resource__pk=resource)

        return qs


class Mutation(SkoleObjectType):
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()
