from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import SchoolType
from skole.utils.shortcuts import get_obj_or_none
from skole.utils.types import ID


class SchoolTypeObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = SchoolType
        fields = ("id", "name")


class Query(graphene.ObjectType):
    school_types = graphene.List(SchoolTypeObjectType)
    school_type = graphene.Field(SchoolTypeObjectType, id=graphene.ID())

    def resolve_school_types(self, info: ResolveInfo) -> "QuerySet[SchoolType]":
        return SchoolType.objects.all()

    def resolve_school_type(
        self, info: ResolveInfo, id: ID = None
    ) -> Optional[SchoolType]:
        return get_obj_or_none(SchoolType, id)
