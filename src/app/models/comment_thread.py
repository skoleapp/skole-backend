from django.db import models

from app.models.course import Course
from app.models.comment import Comment
from app.models.resource import Resource
from app.models.user import User


class CommentThread(models.Model):
    """Base class for all different comment threads."""

    starting_comment = models.OneToOneField(Comment, on_delete=models.PROTECT)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="comment_threads")

    points = models.IntegerField(default=0)

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class CourseCommentThread(CommentThread):
    """Models a comment thread posted on a course."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="comment_threads")


class ResourceCommentThread(CommentThread):
    """Models a comment thread posted on a resource."""

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="comment_threads")
