import graphene
from graphene_django import DjangoObjectType

from skole.models import Activity


class ActivityObjectType(DjangoObjectType):
    description = graphene.String()

    class Meta:
        model = Activity
        fields = ("target_user", "description")
