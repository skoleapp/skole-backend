from django.db import models

from app.models import Comment, Resource, ResourcePart, Vote


class DeleteObjectModel(models.Model):
    """A helper model used to provide graphene.ID() fields for DeleteObjectForm."""

    comment = models.OneToOneField(Comment, on_delete=models.DO_NOTHING)
    resource = models.OneToOneField(Resource, on_delete=models.DO_NOTHING)
    resource_part = models.OneToOneField(ResourcePart, on_delete=models.DO_NOTHING)
    vote = models.OneToOneField(Vote, on_delete=models.DO_NOTHING)
