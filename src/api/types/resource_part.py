from graphene_django import DjangoObjectType

from app.models import ResourcePart


class ResourcePartType(DjangoObjectType):
    class Meta:
        model = ResourcePart
        fields = ("id", "resource")
