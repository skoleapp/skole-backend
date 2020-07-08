import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import Activity


class ActivityObjectType(DjangoObjectType):
    name = graphene.String()
    description = graphene.String()

    class Meta:
        model = Activity
        fields = ("name", "description", "target_user", "course", "resource", "comment")

    def resolve_name(self, info: ResolveInfo) -> str:
        return self.activity_type.name

    def resolve_description(self, info: ResolveInfo) -> str:
        return self.activity_type.description
