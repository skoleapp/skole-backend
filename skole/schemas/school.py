from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import School
from skole.schemas.city import CityObjectType
from skole.schemas.country import CountryObjectType
from skole.schemas.school_type import SchoolTypeObjectType
from skole.schemas.subject import SubjectObjectType
from skole.utils.shortcuts import get_obj_or_none


class SchoolObjectType(DjangoObjectType):
    name = graphene.String()
    school_type = graphene.Field(SchoolTypeObjectType)
    city = graphene.Field(CityObjectType)
    country = graphene.Field(CountryObjectType)
    subjects = graphene.List(SubjectObjectType)

    class Meta:
        model = School
        fields = (
            "id",
            "name",
            "school_type",
            "city",
            "country",
            "subjects",
            "courses",
        )

    def resolve_country(self, info: ResolveInfo) -> str:
        return self.city.country


class Query(graphene.ObjectType):
    schools = graphene.List(SchoolObjectType)
    school = graphene.Field(SchoolObjectType, id=graphene.ID())

    def resolve_schools(self, info: ResolveInfo) -> "QuerySet[School]":
        assert info.context is not None
        return School.objects.translated(info.context.LANGUAGE_CODE).order_by(
            "translations__name"
        )

    def resolve_school(
        self, info: ResolveInfo, id: Optional[int] = None
    ) -> Optional[School]:
        return get_obj_or_none(School, id)
