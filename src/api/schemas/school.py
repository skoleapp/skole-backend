from typing import List

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from core.models import School


class SchoolType(DjangoObjectType):
    school_type = graphene.String()

    class Meta:
        model = School
        fields = ("id", "school_type", "name", "city", "country", "subjects")

    def resolve_school_type(self, info: ResolveInfo) -> str:
        return self.get_school_type_display()


class Query(graphene.ObjectType):
    school_list = graphene.List(SchoolType)
    school = graphene.Field(SchoolType, id=graphene.Int())

    def resolve_school_list(self, info: ResolveInfo) -> List[School]:
        return School.objects.all()

    def resolve_school(self, info: ResolveInfo, id: int) -> School:
        return School.objects.get(pk=id)
