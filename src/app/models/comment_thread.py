from django.db import models


class CommentThread(models.Model):
    """Models a comment thread posted on a course."""
    foo = models.CharField(max_length=30)
