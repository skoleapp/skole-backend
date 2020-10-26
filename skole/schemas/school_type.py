from typing import Optional

import graphene
from django.conf import settings
from django.db.models import QuerySet
from graphene_django import DjangoObjectType

from skole.models import SchoolType
from skole.types import ID, ResolveInfo
from skole.utils.api_descriptions import APIDescriptions


class SchoolTypeObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = SchoolType
        description = APIDescriptions.SCHOOL_TYPE_OBJECT_TYPE
        fields = ("id", "name")


class Query(graphene.ObjectType):
    autocomplete_school_types = graphene.List(
        SchoolTypeObjectType, description=APIDescriptions.AUTOCOMPLETE_SCHOOL_TYPES,
    )

    school_type = graphene.Field(
        SchoolTypeObjectType,
        id=graphene.ID(),
        description=APIDescriptions.DETAIL_QUERY,
    )

    @staticmethod
    def resolve_autocomplete_school_types(
        root: None, info: ResolveInfo
    ) -> QuerySet[SchoolType]:
        return SchoolType.objects.all()[: settings.AUTOCOMPLETE_MAX_RESULTS]

    @staticmethod
    def resolve_school_type(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[SchoolType]:
        return SchoolType.objects.get_or_none(pk=id)
