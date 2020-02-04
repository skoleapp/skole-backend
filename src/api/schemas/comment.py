from typing import Any, Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import GraphQLError, ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.comment import CreateCommentForm, UpdateCommentForm
from api.schemas.resource_part import ResourcePartObjectType
from api.utils.common import get_obj_or_none
from api.utils.messages import NOT_OWNER_MESSAGE
from api.utils.points import (
    POINTS_COMMENT_REPLY_MULTIPLIER,
    POINTS_COURSE_COMMENT_MULTIPLIER,
    POINTS_RESOURCE_COMMENT_MULTIPLIER,
    get_points_for_target,
)
from app.models import Comment, Course, Resource, ResourcePart


class CommentObjectType(DjangoObjectType):
    points = graphene.Int()
    resource_part = graphene.Field(ResourcePartObjectType)
    reply_count = graphene.Int()
    vote_status = graphene.Int()

    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "text",
            "attachment",
            "course",
            "resource",
            "resource_part",
            "comment",
            "reply_comments",
            "reply_count",
            "modified",
            "created",
        )

    def resolve_points(self, info: ResolveInfo) -> int:
        if self.course is not None:
            return get_points_for_target(self, POINTS_COURSE_COMMENT_MULTIPLIER)
        if self.resource is not None:
            return get_points_for_target(self, POINTS_RESOURCE_COMMENT_MULTIPLIER)
        if self.resource_part is not None:
            return get_points_for_target(self, POINTS_RESOURCE_COMMENT_MULTIPLIER)
        if self.comment is not None:
            return get_points_for_target(self.comment, POINTS_COMMENT_REPLY_MULTIPLIER)

        raise AssertionError("All foreign keys of the Comment were null.")

    def resolve_vote_status(self, info: ResolveInfo) -> Optional[int]:
        """Resolve current user's vote status if it exists."""
        user = info.context.user

        if user.is_anonymous:
            return None

        vote = self.votes.get(user=user)

        if vote is not None:
            return vote.status
        else:
            return None


class CreateCommentMutation(DjangoModelFormMutation):
    comments = graphene.List(CommentObjectType)

    class Meta:
        form_class = CreateCommentForm
        return_field_name = "comments"

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: CreateCommentForm, info: ResolveInfo
    ) -> "CreateCommentMutation":
        if file := info.context.FILES.get("1"):
            form.cleaned_data["attachment"] = file

        Comment.objects.create_comment(user=info.context.user, **form.cleaned_data)

        target = form.cleaned_data["target"]

        if isinstance(target, Course):
            comments = Comment.objects.filter(course=target)
        elif isinstance(target, Resource):
            comments = Comment.objects.filter(resource=target)
        elif isinstance(target, ResourcePart):
            comments = Comment.objects.filter(resource_part=target)
        elif isinstance(target, Comment):
            comments = Comment.objects.filter(comment=target)
        else:
            # This should never happend because a validation error is thrown in the form.
            comments = Comment.objects.none()

        return cls(comments=comments)


class UpdateCommentMutation(DjangoModelFormMutation):
    comment = graphene.Field(CommentObjectType)

    class Meta:
        form_class = UpdateCommentForm

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: UpdateCommentForm, info: ResolveInfo
    ) -> "UpdateCommentMutation":

        comment = Comment.objects.get(pk=form.cleaned_data.pop("comment_id"))

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


class Query(graphene.ObjectType):
    comment = graphene.Field(CommentObjectType, comment_id=graphene.Int())

    def resolve_comment(self, info: ResolveInfo, comment_id: int) -> Optional[Comment]:
        return get_obj_or_none(Comment, comment_id)


class Mutation(graphene.ObjectType):
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
