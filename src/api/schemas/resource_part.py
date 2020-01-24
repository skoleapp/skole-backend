from graphene_django import DjangoObjectType

from app.models import ResourcePart


class ResourcePartObjectType(DjangoObjectType):
    class Meta:
        model = ResourcePart
        fields = ("id", "title", "file", "text", "file")
