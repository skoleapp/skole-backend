from typing import Optional

import graphene
from django.conf import settings
from django.db.models import Count, QuerySet
from graphene_django import DjangoObjectType

from skole.models import Country, School
from skole.schemas.city import CityObjectType
from skole.schemas.country import CountryObjectType
from skole.schemas.school_type import SchoolTypeObjectType
from skole.schemas.subject import SubjectObjectType
from skole.types import ID, ResolveInfo
from skole.utils import api_descriptions


class SchoolObjectType(DjangoObjectType):
    name = graphene.String()
    school_type = graphene.Field(SchoolTypeObjectType)
    city = graphene.Field(CityObjectType)
    country = graphene.Field(CountryObjectType)
    subjects = graphene.List(SubjectObjectType)

    class Meta:
        model = School
        description = api_descriptions.SCHOOL_OBJECT_TYPE
        fields = (
            "id",
            "name",
            "school_type",
            "city",
            "country",
            "subjects",
            "courses",
        )

    @staticmethod
    def resolve_country(root: School, info: ResolveInfo) -> Country:
        return root.city.country


class Query(graphene.ObjectType):
    autocomplete_schools = graphene.List(
        SchoolObjectType,
        name=graphene.String(),
        description=api_descriptions.AUTOCOMPLETE_SCHOOLS,
    )

    school = graphene.Field(
        SchoolObjectType, id=graphene.ID(), description=api_descriptions.DETAIL_QUERY,
    )

    @staticmethod
    def resolve_autocomplete_schools(
        root: None, info: ResolveInfo, name: str = ""
    ) -> QuerySet[School]:
        qs = School.objects.translated()

        if name != "":
            qs = qs.filter(translations__name__icontains=name)

        qs = qs.annotate(num_courses=Count("courses")).order_by(
            "-num_courses", "translations__name"
        )

        return qs[: settings.AUTOCOMPLETE_MAX_RESULTS]

    @staticmethod
    def resolve_school(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[School]:
        return School.objects.get_or_none(pk=id)
