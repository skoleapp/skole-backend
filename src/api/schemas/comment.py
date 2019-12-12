from typing import Optional, List

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.utils.vote import AbstractUpvoteMutation, AbstractDownvoteMutation
from app.models import Comment
from api.utils.points import get_points_for_target, POINTS_COURSE_COMMENT_MULTIPLIER, POINTS_RESOURCE_COMMENT_MULTIPLIER



class CommentType(DjangoObjectType):
    points = graphene.Int()

    class Meta:
        model = Comment
        fields = ("id", "creator", "text", "attachment", "course",
                  "resource", "resource_part", "modified", "created")

    def resolve_points(self, info: ResolveInfo) -> int:
        if self.course is not None:
            return get_points_for_target(self, POINTS_COURSE_COMMENT_MULTIPLIER)
        if self.resource is not None:
            return get_points_for_target(self, POINTS_RESOURCE_COMMENT_MULTIPLIER)
        if self.resource_part is not None:
            return get_points_for_target(self, POINTS_RESOURCE_COMMENT_MULTIPLIER)
        raise AssertionError("All foreign keys of Comment were null.")


class UpvoteCommentMutation(AbstractUpvoteMutation):
    class Input:
        comment_id = graphene.Int()

    comment = graphene.Field(CommentType)


class DownvoteCommentMutation(AbstractDownvoteMutation):
    class Input:
        comment_id = graphene.Int()

    comment = graphene.Field(CommentType)


class Query(graphene.ObjectType):
    comments = graphene.List(
        CommentType,
        course_id=graphene.String(),
        resource_id=graphene.Int(),
        resource_part_id=graphene.Int(),
    )
    comment = graphene.Field(CommentType, comment_id=graphene.Int())

    def resolve_comments(self, info: ResolveInfo, course_id: Optional[int] = None,
                         resource_id: Optional[int] = None,
                         resource_part_id: Optional[int] = None) -> List[Comment]:

        comments = Comment.objects.all()

        if course_id is not None:
            comments = comments.filter(course__pk=course_id)
        if resource_id is not None:
            comments = comments.filter(resource__pk=resource_id)
        if resource_part_id is not None:
            comments = comments.filter(resource_part__pk=resource_part_id)

        return comments

    def resolve_comment(self, info: ResolveInfo, comment_id: int) -> Comment:
        return Comment.objects.get(pk=comment_id)


class Mutation(graphene.ObjectType):
    upvote_comment = UpvoteCommentMutation.Field()
    downvote_comment = DownvoteCommentMutation.Field()
