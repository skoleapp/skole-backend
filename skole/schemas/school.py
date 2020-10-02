from typing import Optional

import graphene
from django.db.models import Count, QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import School
from skole.schemas.city import CityObjectType
from skole.schemas.country import CountryObjectType
from skole.schemas.school_type import SchoolTypeObjectType
from skole.schemas.subject import SubjectObjectType
from skole.types import ID
from skole.utils.constants import MAX_QUERY_RESULTS
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
    # Used for non-paginated queries such as auto complete field results.
    schools = graphene.List(SchoolObjectType, name=graphene.String())
    school = graphene.Field(SchoolObjectType, id=graphene.ID())

    # We want to avoid making massive queries for instance in auto complete fields so we slice the results from this non-paginated query.
    # If no school name is provided as a parameter, we return only the schools that have the most courses so that at least some results are always returned.
    def resolve_schools(self, info: ResolveInfo, name: str = "") -> "QuerySet[School]":
        assert info.context is not None
        qs = School.objects.translated(info.context.LANGUAGE_CODE).order_by(
            "translations__name"
        )

        if name != "":
            qs = qs.filter(
                translations__name__icontains=name,
                translations__language_code=info.context.LANGUAGE_CODE,
            )

        qs = qs.annotate(num_courses=Count("courses")).order_by("-num_courses")
        return qs[:MAX_QUERY_RESULTS]

    def resolve_school(self, info: ResolveInfo, id: ID = None) -> Optional[School]:
        return get_obj_or_none(School, id)
