import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import CreateCommentForm, DeleteCommentForm, UpdateCommentForm
from skole.models import Comment
from skole.schemas.base import (
    SkoleCreateUpdateMutationMixin,
    SkoleDeleteMutationMixin,
    SkoleObjectType,
)
from skole.schemas.mixins import SuccessMessageMixin, VoteMixin
from skole.types import ResolveInfo
from skole.utils.constants import Messages


class CommentObjectType(VoteMixin, DjangoObjectType):
    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "text",
            "attachment",
            "course",
            "resource",
            "comment",
            "reply_comments",
            "score",
            "modified",
            "created",
        )

    @staticmethod
    def resolve_attachment(root: Comment, info: ResolveInfo) -> str:
        return root.attachment.url if root.attachment else ""


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


class Mutation(SkoleObjectType):
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()
