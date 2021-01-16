import random
from typing import List, Union

import graphene
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet

from skole.models import Comment, Course, Resource, User
from skole.schemas.base import SkoleObjectType
from skole.schemas.comment import CommentObjectType
from skole.schemas.course import CourseObjectType
from skole.schemas.resource import ResourceObjectType
from skole.types import ResolveInfo


def get_suggestions(
    user: [Union[User, AnonymousUser]], num_results: int
) -> List[Union[Course, Resource, Comment]]:
    """
    Courses, resources and comments each get a cut of third of the total amount. Get
    courses and resources that have been commented most recently and the newest
    comments.

    If the user is logged in, exclude the following items:

    - Courses and resources that have been starred, voted, commented by the user.
    - Courses and resources which reply comments from the user.
    - Comments that have been made, starred, voted or replied by the user.
    """

    cut = num_results / 3

    if user.is_anonymous:
        course_qs = Course.objects.filter(comment_count__gt=0).order_by(
            "-comment_count"
        )[:cut]

        resource_qs = Resource.objects.filter(comment_count__gt=0).order_by(
            "-comment_count"
        )[:cut]

        comment_qs = Comment.objects.order_by("-pk")[:cut]

    else:
        course_qs = Course.objects.filter(comment_count__gte=1).exclude(
            user=user,
            stars__user=user,
            votes__user=user,
            comments__user=user,
            comments__reply_comments__user=user,
        )[:cut]

        resource_qs = Resource.objects.filter(comment_count__gte=1).exclude(
            user=user,
            stars__user=user,
            votes__user=user,
            comments__user=user,
            comments__reply_comments__user=user,
        )[:cut]

        comment_qs = Comment.objects.order_by("-pk").exclude(
            user=user, reply_comments__user=user, votes__user=user
        )[:cut]

    results = [*course_qs, *resource_qs, *comment_qs]
    random.shuffle(results)
    return results


class SuggestionsUnion(graphene.Union):
    class Meta:
        types = (CourseObjectType, ResourceObjectType, CommentObjectType)


class Query(SkoleObjectType):
    suggestions = graphene.List(SuggestionsUnion)
    suggestions_preview = graphene.List(SuggestionsUnion)

    @staticmethod
    def resolve_suggestions(
        root: None, info: ResolveInfo
    ) -> QuerySet[Union[Course, Resource, Comment]]:
        """Return suggested courses, resources and comments based on secret Skole AI-
        powered algorithms."""

        user = info.context.user
        return get_suggestions(user, settings.SUGGESTIONS_COUNT)

    @staticmethod
    def resolve_suggestions_preview(
        root: None, info: ResolveInfo
    ) -> QuerySet[Union[Course, Resource, Comment]]:
        """Return preview of the suggestions."""

        user = info.context.user
        return get_suggestions(user, settings.SUGGESTIONS_PREVIEW_COUNT)
