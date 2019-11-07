from graphene_django import DjangoObjectType

from app.models import ResourceComment


class ResourceCommentType(DjangoObjectType):
    class Meta:
        model = ResourceComment
        fields = ("id", "text", "attachment", "resource", "creator", "points", "modified", "created")
