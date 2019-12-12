from typing import List

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from app.models import SchoolType


class SchoolTypeObjectType(DjangoObjectType):
    class Meta:
        model = SchoolType
        fields = ("id", "name")


class Query(graphene.ObjectType):
    school_types = graphene.List(SchoolTypeObjectType)

    def resolve_school_types(self, info: ResolveInfo) -> List[SchoolType]:
        return SchoolType.objects.all()
