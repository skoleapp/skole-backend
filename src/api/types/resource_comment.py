from graphene_django import DjangoObjectType

from core.models import ResourceComment


class ResourceCommentType(DjangoObjectType):
    class Meta:
        model = ResourceComment
        fields = ("id", "text", "attachment", "resource", "creator", "points", "modified", "created")
