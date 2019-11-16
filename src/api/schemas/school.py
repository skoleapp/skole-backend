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


class Query(graphene.ObjectType):
    schools = graphene.List(
        SchoolType,
        school_type=graphene.String(),
        city=graphene.String(),
        country=graphene.String(),
        name=graphene.String()
    )
    
    school = graphene.Field(SchoolType, school_id=graphene.Int())

    def resolve_schools(
        self,
        info: ResolveInfo,
        school_type: str = None,
        city: str = None,
        country: str = None,
        name: str = None
    ) -> List[School]:
        schools =  School.objects.all()

        if school_type is not None:
            schools = schools.filter(school_type=school_type.replace(" ", "_").upper()) # Convert to upper snake case.
        if city is not None:
            schools = schools.filter(city__iexact=city)
        if country is not None:
            schools = schools.filter(country__iexact=country)
        if name is not None:
            schools = schools.filter(name__icontains=name)
        
        return schools

    def resolve_school(self, info: ResolveInfo, school_id: int = None) -> School:
        if school_id is not None:
            return School.objects.get(pk=school_id)
        else:
            return None
