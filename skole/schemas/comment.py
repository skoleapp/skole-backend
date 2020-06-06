import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo

from skole.forms.comment import CreateCommentForm, DeleteCommentForm, UpdateCommentForm
from skole.models import Comment
from skole.utils.constants import Messages, MutationErrors
from skole.utils.mixins import (
    DeleteMutationMixin,
    FileMutationMixin,
    MessageMixin,
    VerificationRequiredMutationMixin,
    VoteMixin,
)


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


class CreateCommentMutation(
    VerificationRequiredMutationMixin,
    FileMutationMixin,
    MessageMixin,
    DjangoModelFormMutation,
):
    class Meta:
        form_class = CreateCommentForm
        exclude_fields = ("id",)

    @classmethod
    def perform_mutate(
        cls, form: CreateCommentForm, info: ResolveInfo
    ) -> "CreateCommentMutation":
        assert info.context is not None

        if form.cleaned_data["attachment"] == "" and form.cleaned_data["text"] == "":
            return cls(errors=MutationErrors.COMMENT_EMPTY)

        comment = Comment.objects.create_comment(
            user=info.context.user, **form.cleaned_data
        )

        return cls(comment=comment, message=Messages.MESSAGE_SENT)


class UpdateCommentMutation(
    VerificationRequiredMutationMixin,
    FileMutationMixin,
    MessageMixin,
    DjangoModelFormMutation,
):
    comment = graphene.Field(CommentObjectType)

    class Meta:
        form_class = UpdateCommentForm

    @classmethod
    def perform_mutate(
        cls, form: UpdateCommentForm, info: ResolveInfo
    ) -> "UpdateCommentMutation":
        assert info.context is not None
        comment = form.instance

        if comment.user != info.context.user:
            return cls(errors=MutationErrors.NOT_OWNER)

        Comment.objects.update_comment(comment, **form.cleaned_data)
        return cls(comment=comment, message=Messages.COMMENT_UPDATED)


class DeleteCommentMutation(DeleteMutationMixin, DjangoModelFormMutation):
    class Meta(DeleteMutationMixin.Meta):
        form_class = DeleteCommentForm

    @staticmethod
    def get_success_message() -> str:
        return Messages.COMMENT_DELETED


class Mutation(graphene.ObjectType):
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()
