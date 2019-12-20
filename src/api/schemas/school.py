from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from app.models import School, Country


class SchoolType(DjangoObjectType):
    school_type = graphene.String()
    city = graphene.String()
    country = graphene.String()
    subject_count = graphene.Int()
    course_count = graphene.Int()

    class Meta:
        model = School
        fields = ("id", "name", "city")

    def resolve_country(self, info: ResolveInfo) -> Country:
        return self.city.country

    def resolve_subject_count(self, info: ResolveInfo) -> int:
        return self.subjects.count()

    def resolve_course_count(self, info: ResolveInfo) -> int:
        return self.courses.count()


class Query(graphene.ObjectType):
    schools = graphene.List(SchoolType)
    school = graphene.Field(SchoolType, school_id=graphene.Int())

    def resolve_schools(self, info: ResolveInfo) -> List[School]:
        return School.objects.all()

    def resolve_school(self, info: ResolveInfo, school_id: int) -> School:
        return School.objects.get(pk=school_id)
