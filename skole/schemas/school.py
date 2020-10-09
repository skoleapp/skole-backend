from typing import Optional

import graphene
from django.conf import settings
from django.db.models import Count, QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import Country, School
from skole.schemas.city import CityObjectType
from skole.schemas.country import CountryObjectType
from skole.schemas.school_type import SchoolTypeObjectType
from skole.schemas.subject import SubjectObjectType
from skole.types import ID


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

    @staticmethod
    def resolve_country(root: School, info: ResolveInfo) -> Country:
        return root.city.country


class Query(graphene.ObjectType):
    autocomplete_schools = graphene.List(SchoolObjectType, name=graphene.String())
    school = graphene.Field(SchoolObjectType, id=graphene.ID())

    @staticmethod
    def resolve_autocomplete_schools(
        root: None, info: ResolveInfo, name: str = ""
    ) -> QuerySet[School]:
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
        return qs[: settings.AUTOCOMPLETE_MAX_RESULTS]

    @staticmethod
    def resolve_school(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[School]:
        return School.objects.get_or_none(pk=id)
