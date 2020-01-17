from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from app.models import School, SchoolType as SchoolTypeModel, Country


class SchoolType(DjangoObjectType):
    school_type = graphene.String()
    city = graphene.String()
    country = graphene.String()
    subject_count = graphene.Int()
    course_count = graphene.Int()

    class Meta:
        model = School
        fields = ("id", "name")

    def resolve_country(self, info: ResolveInfo) -> Country:
        return self.city.country

    def resolve_subject_count(self, info: ResolveInfo) -> int:
        return self.subjects.count()

    def resolve_course_count(self, info: ResolveInfo) -> int:
        return self.courses.count()


class SchoolTypeObjectType(DjangoObjectType):
    class Meta:
        model = SchoolTypeModel
        fields = ("id", "name")


class Query(graphene.ObjectType):
    schools = graphene.List(SchoolType)
    school_types = graphene.List(SchoolTypeObjectType)
    school = graphene.Field(SchoolType, school_id=graphene.Int())
    school_type = graphene.Field(SchoolTypeObjectType, school_type_id=graphene.Int())

    def resolve_schools(self, info: ResolveInfo) -> List[School]:
        return School.objects.order_by("name")

    def resolve_school_types(self, info: ResolveInfo) -> List[SchoolType]:
        return SchoolType.objects.all()

    def resolve_school(
        self, info: ResolveInfo, school_id: Optional[int] = None
    ) -> School:
        try:
            return School.objects.get(pk=school_id)
        except School.DoesNotExist:
            """Return 'None' instead of throwing a GraphQL Error."""
            return None

    def resolve_school_type(
        self, info: ResolveInfo, school_type_id: Optional[int] = None
    ) -> SchoolTypeModel:
        try:
            return SchoolTypeModel.objects.get(pk=school_type_id)
        except SchoolTypeModel.DoesNotExist:
            """Return 'None' instead of throwing a GraphQL Error."""
            return None
