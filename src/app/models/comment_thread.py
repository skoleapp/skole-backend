from django.db import models

from .course import Course
from .resource import Resource


class CourseCommentThread(models.Model):
    """Models a comment thread posted on a course."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_comment_threads")


class ResourceCommentThread(models.Model):
    """Models a comment thread posted on a resource."""

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="resource_comment_threads")
