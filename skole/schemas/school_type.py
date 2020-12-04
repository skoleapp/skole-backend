from typing import Optional

import graphene
from django.conf import settings
from django.db.models import QuerySet

from skole.models import SchoolType
from skole.schemas.base import SkoleDjangoObjectType, SkoleObjectType
from skole.types import ID, ResolveInfo


class SchoolTypeObjectType(SkoleDjangoObjectType):
    name = graphene.String()

    class Meta:
        model = SchoolType
        fields = ("id", "name")


class Query(SkoleObjectType):
    autocomplete_school_types = graphene.List(SchoolTypeObjectType)
    school_type = graphene.Field(SchoolTypeObjectType, id=graphene.ID())

    @staticmethod
    def resolve_autocomplete_school_types(
        root: None, info: ResolveInfo
    ) -> QuerySet[SchoolType]:
        """Results are sorted by creation time."""
        return SchoolType.objects.all()[: settings.AUTOCOMPLETE_MAX_RESULTS]

    @staticmethod
    def resolve_school_type(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[SchoolType]:
        return SchoolType.objects.get_or_none(pk=id)
