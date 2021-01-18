import random
from typing import List, Union

import graphene
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from skole.models import Comment, Course, Resource, SkoleModel, User
from skole.schemas.base import SkoleObjectType
from skole.schemas.comment import CommentObjectType
from skole.schemas.course import CourseObjectType
from skole.schemas.resource import ResourceObjectType
from skole.types import ResolveInfo


def get_suggestions(
    user: Union[User, AnonymousUser], num_results: int
) -> List[SkoleModel]:
    """
    Courses, resources and comments each get a cut of third of the total amount. Get
    courses and resources that have been commented most recently and the newest comments
    that are not replies and do not have a negative score.

    Exclude courses and resources which comments are already included in the suggestions.
    In addition, if the user is logged in, exclude the following items:

    - Courses and resources that have been starred, voted, commented by the user.
    - Courses and resources which reply comments from the user.
    - Comments that have been made, starred, voted or replied by the user.
    """

    cut = int(num_results / 3)

    # Ignore: All of the ignores below exist due to Mypy not inferring types from the model classes.

    if user.is_anonymous:
        comment_qs = Comment.objects.filter(comment=None, score__gte=0).order_by("-pk")[  # type: ignore[misc]
            :cut
        ]

        course_qs = (
            Course.objects.exclude(comments__in=comment_qs)
            .filter(comment_count__gt=0)  # type: ignore[misc]
            .order_by("-comments__pk")[:cut]
        )

        resource_qs = (
            Resource.objects.exclude(comments__in=comment_qs)
            .filter(comment_count__gt=0)  # type: ignore[misc]
            .order_by("-comments__pk")[:cut]
        )

    else:
        comment_qs = (
            Comment.objects.filter(comment=None, score__gte=0)  # type: ignore[misc]
            .exclude(
                user=user,
                reply_comments__user=user,
                votes__user=user,
            )
            .order_by("-pk")[:cut]
        )

        course_qs = (
            Course.objects.exclude(
                comments__in=comment_qs,
                user=user,
                stars__user=user,
                votes__user=user,
                comments__user=user,
                comments__reply_comments__user=user,
            )
            .filter(comment_count__gt=0)  # type: ignore[misc]
            .order_by("-comments__pk")[:cut]
        )

        resource_qs = (
            Resource.objects.exclude(
                comments__in=comment_qs,
                user=user,
                stars__user=user,
                votes__user=user,
                comments__user=user,
                comments__reply_comments__user=user,
            )
            .filter(comment_count__gt=0)  # type: ignore[misc]
            .order_by("-comments__pk")[:cut]
        )

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
    def resolve_suggestions(root: None, info: ResolveInfo) -> List[SkoleModel]:
        """Return suggested courses, resources and comments based on secret Skole AI-
        powered algorithms."""

        user = info.context.user
        return get_suggestions(user, settings.SUGGESTIONS_COUNT)

    @staticmethod
    def resolve_suggestions_preview(root: None, info: ResolveInfo) -> List[SkoleModel]:
        """Return preview of the suggestions."""

        user = info.context.user
        return get_suggestions(user, settings.SUGGESTIONS_PREVIEW_COUNT)
