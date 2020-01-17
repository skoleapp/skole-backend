from typing import Any, Union

from django.db import models
from django.db.models.functions import Coalesce

from app.models import User, Resource, Course, Comment

POINTS_RESOURCE_MULTIPLIER = 10
POINTS_COURSE_MULTIPLIER = 5
POINTS_RESOURCE_COMMENT_MULTIPLIER = 1
POINTS_COURSE_COMMENT_MULTIPLIER = 1


def aggregate(model: Any, field_name: str, multiplier: int) -> int:
    return (
        model.aggregate(points=Coalesce(models.Sum(field_name), 0))["points"]
        * multiplier
    )


def get_points_for_user(user: User) -> int:
    """Return all the summed up points of the user's created items."""
    points = 0

    points += aggregate(user.created_courses, "votes__status", POINTS_COURSE_MULTIPLIER)
    points += aggregate(
        user.created_resources, "votes__status", POINTS_RESOURCE_MULTIPLIER
    )
    points += aggregate(
        user.comments,
        "course__comments__votes__status",
        POINTS_COURSE_COMMENT_MULTIPLIER,
    )
    points += aggregate(
        user.comments,
        "resource__comments__votes__status",
        POINTS_RESOURCE_COMMENT_MULTIPLIER,
    )
    points += aggregate(
        user.comments,
        "resource_part__comments__votes__status",
        POINTS_RESOURCE_COMMENT_MULTIPLIER,
    )

    return points


def get_points_for_target(
    target: Union[Comment, Course, Resource], multiplier: int
) -> int:
    return aggregate(target.votes, "status", multiplier)
