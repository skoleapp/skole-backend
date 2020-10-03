from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import SchoolType
from skole.types import ID
from skole.utils.shortcuts import get_obj_or_none


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
    ) -> "QuerySet[SchoolType]":
        """Used for queries made by the client's auto complete fields."""
        return SchoolType.objects.all()

    def resolve_school_type(
        self, info: ResolveInfo, id: ID = None
    ) -> Optional[SchoolType]:
        return get_obj_or_none(SchoolType, id)
