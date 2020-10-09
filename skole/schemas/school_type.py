from typing import Optional

import graphene
from django.conf import settings
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import SchoolType
from skole.types import ID


class SchoolTypeObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = SchoolType
        fields = ("id", "name")


class Query(graphene.ObjectType):
    autocomplete_school_types = graphene.List(SchoolTypeObjectType)
    school_type = graphene.Field(SchoolTypeObjectType, id=graphene.ID())

    def resolve_autocomplete_school_types(
        self, info: ResolveInfo
    ) -> QuerySet[SchoolType]:
        """
        Used for queries made by the client's auto complete fields.

        We want to avoid making massive queries by limiting the amount of results.
        """
        return SchoolType.objects.all()[: settings.AUTOCOMPLETE_MAX_RESULTS]

    def resolve_school_type(
        self, info: ResolveInfo, id: ID = None
    ) -> Optional[SchoolType]:
        return SchoolType.objects.get_or_none(pk=id)
