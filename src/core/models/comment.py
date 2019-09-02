from django.db import models

from .user import User

class Comment(models.Model):
    text = models.CharField(max_length=10000)
    attachment = models.FileField(upload_to="uploads/comment_attachments")
    points = models.IntegerField(default=0)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.creator.username}: {self.text}"
