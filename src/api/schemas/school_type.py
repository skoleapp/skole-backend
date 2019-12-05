import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo
from app.models import SchoolType
from typing import List


class SchoolTypeObjectType(DjangoObjectType):
    class Meta:
        model = SchoolType
        fields = ("name",)


class Query(graphene.ObjectType):
    school_types = graphene.List(SchoolTypeObjectType)

    def resolve_school_types(self, info: ResolveInfo) -> List[SchoolType]:
        return SchoolType.objects.all()
