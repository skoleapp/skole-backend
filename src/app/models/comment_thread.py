from django.db import models


class CommentThread(models.Model):
    """Models a comment thread posted on a course."""
    temp = models.CharField(max_length=1)
