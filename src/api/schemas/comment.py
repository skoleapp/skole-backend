from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.forms.comment import CreateCommentForm, UpdateCommentForm
from api.utils.points import (
    POINTS_COURSE_COMMENT_MULTIPLIER,
    POINTS_RESOURCE_COMMENT_MULTIPLIER,
    get_points_for_target,
)
from api.utils.vote import AbstractDownvoteMutation, AbstractUpvoteMutation
from app.models import Comment


class CommentObjectType(DjangoObjectType):
    points = graphene.Int()

    class Meta:
        model = Comment
        fields = (
            "id",
            "creator",
            "text",
            "attachment",
            "course",
            "resource",
            "comment",
            "resource_part",
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
            # FIXME: probably doesn't work.
            return self.comment.resolve_points(info)

        raise AssertionError("All foreign keys of the Comment were null.")


class CreateCommentMutation(DjangoModelFormMutation):
    comment = graphene.Field(CommentObjectType)

    class Meta:
        form_class = CreateCommentForm

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: CreateCommentForm, info: ResolveInfo
    ) -> "CreateCommentMutation":
        if file := info.context.FILES.get("1"):
            form.cleaned_data["attachment"] = file

        comment = Comment.objects.create_comment(
            creator=info.context.user, **form.cleaned_data
        )
        return cls(comment=comment)


class UpdateCommentMutation(DjangoModelFormMutation):
    comment = graphene.Field(CommentObjectType)

    class Meta:
        form_class = UpdateCommentForm

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: UpdateCommentForm, info: ResolveInfo
    ) -> "UpdateCommentMutation":
        # FIXME: raises graphql.error.located_error.GraphQLLocatedError instead of a nice user error
        comment = Comment.objects.get(pk=form.cleaned_data["comment_id"])

        if file := info.context.FILES.get("1"):
            form.cleaned_data["attachment"] = file

        comment.text = form.cleaned_data["text"]
        comment.attachment = form.cleaned_data["attachment"]
        comment.save()
        return cls(comment=comment)


class UpvoteCommentMutation(AbstractUpvoteMutation):
    class Arguments:
        comment_id = graphene.Int()

    comment = graphene.Field(CommentObjectType)


class DownvoteCommentMutation(AbstractDownvoteMutation):
    class Arguments:
        comment_id = graphene.Int()

    comment = graphene.Field(CommentObjectType)


class Query(graphene.ObjectType):
    comments = graphene.List(
        CommentObjectType,
        course_id=graphene.String(),
        resource_id=graphene.Int(),
        resource_part_id=graphene.Int(),
    )
    comment = graphene.Field(CommentObjectType, comment_id=graphene.Int())

    def resolve_comments(
        self,
        info: ResolveInfo,
        course_id: Optional[int] = None,
        resource_id: Optional[int] = None,
        resource_part_id: Optional[int] = None,
    ) -> List[Comment]:

        comments = Comment.objects.all()

        if course_id is not None:
            comments = comments.filter(course__pk=course_id)
        if resource_id is not None:
            comments = comments.filter(resource__pk=resource_id)
        if resource_part_id is not None:
            comments = comments.filter(resource_part__pk=resource_part_id)

        return comments

    def resolve_comment(self, info: ResolveInfo, comment_id: int) -> Optional[Comment]:
        try:
            return Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            # Return None instead of throwing a GraphQL Error.
            return None


class Mutation(graphene.ObjectType):
    upvote_comment = UpvoteCommentMutation.Field()
    downvote_comment = DownvoteCommentMutation.Field()
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
