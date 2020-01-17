from typing import List, Optional

import graphene
from app.models import Country, School
from app.models import SchoolType
from graphene_django import DjangoObjectType
from graphql import ResolveInfo


class SchoolObjectType(DjangoObjectType):
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
        model = SchoolType
        fields = ("id", "name")


class Query(graphene.ObjectType):
    schools = graphene.List(SchoolObjectType)
    school_types = graphene.List(SchoolTypeObjectType)
    school = graphene.Field(SchoolObjectType, school_id=graphene.Int())
    school_type = graphene.Field(SchoolTypeObjectType, school_type_id=graphene.Int())

    def resolve_schools(self, info: ResolveInfo) -> List[School]:
        return School.objects.order_by("name")

    def resolve_school_types(self, info: ResolveInfo) -> List[SchoolObjectType]:
        return SchoolType.objects.all()

    def resolve_school(
        self, info: ResolveInfo, school_id: Optional[int] = None
    ) -> Optional[School]:
        try:
            return School.objects.get(pk=school_id)
        except School.DoesNotExist:
            # Return None instead of throwing a GraphQL Error.
            return None

    def resolve_school_type(
        self, info: ResolveInfo, school_type_id: Optional[int] = None
    ) -> Optional[SchoolType]:
        try:
            return SchoolType.objects.get(pk=school_type_id)
        except SchoolType.DoesNotExist:
            # Return None instead of throwing a GraphQL Error.
            return None
