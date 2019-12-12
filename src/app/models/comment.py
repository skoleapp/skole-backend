from typing import Union

from django.db import models

from .course import Course
from .resource import Resource
from .resource_part import ResourcePart
from .user import User


class CommentManager(models.Manager):
    def create_comment(self, creator: User, text: str, attachment: str,
                       target: Union[Course, Resource, ResourcePart]) -> 'Comment':
        if isinstance(target, Course):
            comment = self.model(course=target)
        elif isinstance(target, Resource):
            comment = self.model(resource=target)
        elif isinstance(target, ResourcePart):
            comment = self.model(resource_part=target)
        else:
            raise TypeError(f"Invalid target type for Comment: {type(target)}")

        comment.creator = creator
        comment.text = text
        comment.attachment = attachment

        comment.save()
        return comment


class Comment(models.Model):
    """Models one comment, posted on a comment thread."""

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="comments")
    text = models.TextField(max_length=10000)
    attachment = models.FileField(upload_to="uploads/comment_attachments", null=True)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, related_name="comments")
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, related_name="comments")
    resource_part = models.ForeignKey(ResourcePart, on_delete=models.CASCADE, null=True, related_name="comments")

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    def __str__(self) -> str:
        if len(self.text) > 20:
            return f"{self.creator.username}: {self.text[:20]}..."
        else:
            return f"{self.creator.username}: {self.text}"
