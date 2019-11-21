from typing import List

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo
from api.schemas.subject import SubjectType
from app.models import School


class SchoolType(DjangoObjectType):
    school_type = graphene.String()
    subjects = graphene.List(SubjectType)

    class Meta:
        model = School
        fields = ("id", "school_type", "name", "city", "country")

    def resolve_school_type(self, info: ResolveInfo) -> str:
        return self.get_school_type_display()


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
        schools =  School.objects.all()

        if school_type is not None:
            schools = schools.filter(school_type=school_type.replace(" ", "_").upper()) # Convert to upper snake case.
        if school_name is not None:
            schools = schools.filter(name__icontains=school_name)
        if school_city is not None:
            schools = schools.filter(city__iexact=school_city)
        if school_country is not None:
            schools = schools.filter(country__iexact=school_country)
        
        return schools

    def resolve_school(self, info: ResolveInfo, school_id: int = None) -> School:
        if school_id is not None:
            return School.objects.get(pk=school_id)
        else:
            return None
