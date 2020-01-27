from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from app.models import ResourcePart


class ResourcePartObjectType(DjangoObjectType):
    class Meta:
        model = ResourcePart
        fields = ("id", "title", "file", "text", "file")

    def resolve_file(self, info: ResolveInfo) -> str:
        return f"media/{self.file}"
