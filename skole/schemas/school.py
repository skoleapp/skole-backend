from typing import Optional

import graphene
from django.conf import settings
from django.db.models import QuerySet

from skole.models import Country, School
from skole.schemas.base import SkoleDjangoObjectType, SkoleObjectType
from skole.schemas.city import CityObjectType
from skole.schemas.country import CountryObjectType
from skole.schemas.school_type import SchoolTypeObjectType
from skole.schemas.subject import SubjectObjectType
from skole.types import ID, ResolveInfo


class SchoolObjectType(SkoleDjangoObjectType):
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


class Query(SkoleObjectType):
    autocomplete_schools = graphene.List(SchoolObjectType, name=graphene.String())
    school = graphene.Field(SchoolObjectType, id=graphene.ID())

    @staticmethod
    def resolve_autocomplete_schools(
        root: None, info: ResolveInfo, name: str = ""
    ) -> QuerySet[School]:
        """Results are sorted alphabetically."""
        if name != "":
            qs = School.objects.translated(name__icontains=name)
        else:
            qs = School.objects.translated()

        qs = qs.order_by("translations__name")

        return qs[: settings.AUTOCOMPLETE_MAX_RESULTS]

    @staticmethod
    def resolve_school(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[School]:
        return School.objects.get_or_none(pk=id)
