from typing import Any

from django.db import models
from django.db.models.functions import Coalesce

from app.models import User


POINTS_RESOURCE_UPVOTED = 10
POINTS_RESOURCE_DOWNVOTED = -10
POINTS_COURSE_UPVOTED = 5
POINTS_COURSE_DOWNVOTED = -5
POINTS_RESOURCE_COMMENT_UPVOTED = 1
POINTS_RESOURCE_COMMENT_DOWNVOTED = -1
POINTS_COURSE_COMMENT_UPVOTED = 1
POINTS_COURSE_COMMENT_DOWNVOTED = -1


def aggregate(model: Any, field_name: str, multiplier: int) -> int:
    return model.aggregate(points=Coalesce(models.Sum(field_name), 0))["points"] * multiplier


def get_points_of_user(user: User) -> int:
    """Return all the summed up points of the user's created items."""
    points = 0

    points += aggregate(user.created_resources, "upvotes", POINTS_RESOURCE_UPVOTED)
    points += aggregate(user.created_courses, "upvotes", POINTS_COURSE_UPVOTED)
    points += aggregate(user.resource_comments, "upvotes", POINTS_RESOURCE_COMMENT_UPVOTED)
    points += aggregate(user.course_comments, "upvotes", POINTS_COURSE_COMMENT_UPVOTED)

    points += aggregate(user.created_resources, "downvotes", POINTS_RESOURCE_DOWNVOTED)
    points += aggregate(user.created_courses, "downvotes", POINTS_COURSE_DOWNVOTED)
    points += aggregate(user.resource_comments, "downvotes", POINTS_RESOURCE_COMMENT_DOWNVOTED)
    points += aggregate(user.course_comments, "downvotes", POINTS_COURSE_COMMENT_DOWNVOTED)

    return points
