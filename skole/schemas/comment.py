import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo

from skole.forms import CreateCommentForm, DeleteCommentForm, UpdateCommentForm
from skole.models import Comment
from skole.schemas.mixins import (
    MessageMixin,
    SkoleDeleteMutationMixin,
    SkoleMutationMixin,
    VoteMixin,
)
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

    def resolve_attachment(self, info: ResolveInfo) -> str:
        return self.attachment.url if self.attachment else ""


class CreateCommentMutation(SkoleMutationMixin, MessageMixin, DjangoModelFormMutation):
    verification_required = True
    response_message = Messages.MESSAGE_SENT

    class Meta:
        form_class = CreateCommentForm
        exclude_fields = ("id",)  # Without this, graphene adds the field on its own.


class UpdateCommentMutation(SkoleMutationMixin, MessageMixin, DjangoModelFormMutation):
    verification_required = True
    response_message = Messages.COMMENT_UPDATED

    comment = graphene.Field(CommentObjectType)

    class Meta:
        form_class = UpdateCommentForm


class DeleteCommentMutation(SkoleDeleteMutationMixin, DjangoModelFormMutation):
    response_message = Messages.COMMENT_DELETED

    class Meta(SkoleDeleteMutationMixin.Meta):
        form_class = DeleteCommentForm


class Mutation(graphene.ObjectType):
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()
