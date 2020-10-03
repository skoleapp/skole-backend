from typing import Optional

import graphene
from django.conf import settings
from django.db.models import Count, QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import School
from skole.schemas.city import CityObjectType
from skole.schemas.country import CountryObjectType
from skole.schemas.school_type import SchoolTypeObjectType
from skole.schemas.subject import SubjectObjectType
from skole.types import ID
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
    auto_complete_schools = graphene.List(SchoolObjectType, name=graphene.String())
    school = graphene.Field(SchoolObjectType, id=graphene.ID())

    def resolve_auto_complete_schools(
        self, info: ResolveInfo, name: str = ""
    ) -> "QuerySet[School]":
        """
        Used for queries made by the client's auto complete fields.

        We want to avoid making massive queries by limiting the amount of results. If no
        school name is provided as a parameter, we return schools with the most courses.
        """

        assert info.context is not None
        qs = School.objects.translated()

        if name != "":
            qs = qs.filter(translations__name__icontains=name)

        qs = qs.annotate(num_courses=Count("courses")).order_by(
            "-num_courses", "translations__name"
        )
        return qs[: settings.MAX_QUERY_RESULTS]

    def resolve_school(self, info: ResolveInfo, id: ID = None) -> Optional[School]:
        return get_obj_or_none(School, id)
