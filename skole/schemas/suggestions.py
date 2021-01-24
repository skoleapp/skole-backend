import random
from typing import TypeVar, Union, cast

import graphene
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet

from skole.models import Comment, Course, Resource, User
from skole.schemas.base import SkoleObjectType
from skole.schemas.comment import CommentObjectType
from skole.schemas.course import CourseObjectType
from skole.schemas.resource import ResourceObjectType
from skole.types import ResolveInfo, SuggestionModel

T = TypeVar("T", bound=SuggestionModel)


def get_suggestions(
    user: Union[User, AnonymousUser], num_results: int
) -> list[SuggestionModel]:
    """
    Return a selection of trending comments, courses, and resources for suggestions.

    Gets a selection of courses and resources that have been commented most recently and
    the newest comments that do not have a negative score.
    """

    def sample(qs: QuerySet[T]) -> list[T]:
        # Don't use `random.sample` since it raises en error if there aren't enough results.
        ls = list(qs[:num_results])
        random.shuffle(ls)
        return ls[: num_results // 3]

    # Ignore: All of the ignores below exist due to Mypy not inferring annotated fields.

    comments = sample(
        Comment.objects.filter(score__gte=0).order_by("-pk")  # type: ignore[misc]
    )

    courses = sample(
        Course.objects.exclude(
            comments__in=comments,
        )
        .filter(comment_count__gt=0)  # type: ignore[misc]
        .order_by("-comments__pk")
    )

    resources = sample(
        Resource.objects.exclude(
            comments__in=comments,
        )
        .filter(comment_count__gt=0)  # type: ignore[misc]
        .order_by("-comments__pk")
    )

    results = [*comments, *courses, *resources]
    random.shuffle(results)
    return cast(list[SuggestionModel], results)


class SuggestionsUnion(graphene.Union):
    class Meta:
        types = (CourseObjectType, ResourceObjectType, CommentObjectType)


class Query(SkoleObjectType):
    suggestions = graphene.List(SuggestionsUnion)
    suggestions_preview = graphene.List(SuggestionsUnion)

    @staticmethod
    def resolve_suggestions(root: None, info: ResolveInfo) -> list[SuggestionModel]:
        """Return suggested courses, resources and comments based on secret Skole AI-
        powered algorithms."""

        user = info.context.user
        return get_suggestions(user, settings.SUGGESTIONS_COUNT)

    @staticmethod
    def resolve_suggestions_preview(
        root: None, info: ResolveInfo
    ) -> list[SuggestionModel]:
        """Return preview of the suggestions."""

        user = info.context.user
        return get_suggestions(user, settings.SUGGESTIONS_PREVIEW_COUNT)
