from typing import Optional

import graphene
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import GraphQLError, ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.comment import CreateCommentForm, DeleteCommentForm, UpdateCommentForm
from api.utils.common import get_obj_or_none
from api.utils.decorators import verification_required_mutation
from api.utils.delete import DeleteMutationMixin
from api.utils.file import FileMixin
from api.utils.messages import NOT_OWNER_MESSAGE
from api.utils.vote import VoteMixin
from core.models import Comment


class CommentObjectType(VoteMixin, DjangoObjectType):
    reply_count = graphene.Int()

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
            "reply_count",
            "modified",
            "created",
        )

    def resolve_attachment(self, info: ResolveInfo) -> str:
        return self.attachment.url if self.attachment else ""


class CreateCommentMutation(FileMixin, DjangoModelFormMutation):
    class Meta:
        form_class = CreateCommentForm
        exclude_fields = ("id",)

    @classmethod
    @verification_required_mutation
    def perform_mutate(
        cls, form: CreateCommentForm, info: ResolveInfo
    ) -> "CreateCommentMutation":
        assert info.context is not None
        if form.cleaned_data["attachment"] == "" and form.cleaned_data["text"] == "":
            raise GraphQLError(_("Comment must include either text or attachment."))

        comment = Comment.objects.create_comment(
            user=info.context.user, **form.cleaned_data
        )

        # Query the new comment to get the annotated reply count.
        comment = Comment.objects.get(pk=comment.pk)
        return cls(comment=comment)


class UpdateCommentMutation(DjangoModelFormMutation):
    comment = graphene.Field(CommentObjectType)

    class Meta:
        form_class = UpdateCommentForm

    @classmethod
    @verification_required_mutation
    def perform_mutate(
        cls, form: UpdateCommentForm, info: ResolveInfo
    ) -> "UpdateCommentMutation":
        comment = Comment.objects.get(pk=form.cleaned_data.pop("id"))
        assert info.context is not None

        if comment.user != info.context.user:
            raise GraphQLError(NOT_OWNER_MESSAGE)

        # Don't allow changing attachment to anything but a File or ""
        if form.cleaned_data["attachment"] != "":
            if file := info.context.FILES.get("1"):
                form.cleaned_data["attachment"] = file
            else:
                form.cleaned_data["attachment"] = comment.attachment

        Comment.objects.update_comment(comment, **form.cleaned_data)
        return cls(comment=comment)


class DeleteCommentMutation(DeleteMutationMixin, DjangoModelFormMutation):
    class Meta(DeleteMutationMixin.Meta):
        form_class = DeleteCommentForm


class Query(graphene.ObjectType):
    comment = graphene.Field(CommentObjectType, id=graphene.ID())

    @login_required
    def resolve_comment(
        self, info: ResolveInfo, id: Optional[int] = None
    ) -> Optional[Comment]:
        return get_obj_or_none(Comment, id)


class Mutation(graphene.ObjectType):
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()
