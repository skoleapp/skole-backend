import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import CreateCommentForm, DeleteCommentForm, UpdateCommentForm
from skole.models import Comment
from skole.schemas.mixins import (
    SkoleCreateUpdateMutationMixin,
    SkoleDeleteMutationMixin,
    SuccessMessageMixin,
    VoteMixin,
)
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
    success_message = Messages.MESSAGE_SENT

    class Meta:
        form_class = CreateCommentForm
        exclude_fields = ("id",)  # Without this, graphene adds the field on its own.


class UpdateCommentMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    verification_required = True
    success_message = Messages.COMMENT_UPDATED

    comment = graphene.Field(CommentObjectType)

    class Meta:
        form_class = UpdateCommentForm


class DeleteCommentMutation(SkoleDeleteMutationMixin, DjangoModelFormMutation):
    success_message = Messages.COMMENT_DELETED

    class Meta(SkoleDeleteMutationMixin.Meta):
        form_class = DeleteCommentForm


class Mutation(graphene.ObjectType):
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()
