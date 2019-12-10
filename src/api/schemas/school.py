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
        fields = ("id", "school_type", "name", "city")

    def resolve_country(self, info: ResolveInfo) -> Country:
        return self.city.country

    def resolve_subject_count(self, info: ResolveInfo) -> int:
        return self.subjects.count()

    def resolve_course_count(self, info: ResolveInfo) -> int:
        return self.courses.count()


class Query(graphene.ObjectType):
    schools = graphene.List(
        SchoolType,
        school_type=graphene.String(),
        school_name=graphene.String(),
        school_city=graphene.String(),
        school_country=graphene.String(),
    )

    school = graphene.Field(SchoolType, school_id=graphene.Int())

    def resolve_schools(
            self,
            info: ResolveInfo,
            school_type: str = None,
            school_name: str = None,
            school_city: str = None,
            school_country: str = None,
    ) -> List[School]:
        schools = School.objects.all()

        if school_type is not None:
            schools = schools.filter(school_type__name=school_type)
        if school_name is not None:
            schools = schools.filter(name__icontains=school_name)
        if school_city is not None:
            schools = schools.filter(city__name__iexact=school_city)
        if school_country is not None:
            schools = schools.filter(city__country__name__iexact=school_country)

        return schools

    def resolve_school(self, info: ResolveInfo, school_id: Optional[int] = None) -> Optional[School]:
        if school_id is not None:
            return School.objects.get(pk=school_id)
        else:
            return None
