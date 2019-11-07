import graphene
from graphene_django import DjangoObjectType

from api.schemas.user import UserTypePublic
from core.models import Resource


class ResourceType(DjangoObjectType):
    creator = graphene.Field(UserTypePublic)

    class Meta:
        model = Resource
        fields = ("id", "title", "resource_type", "file", "date", "course", "creator", "points", "modified", "created")
