from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.utils.common import get_obj_or_none
from app.models import SchoolType


class SchoolTypeObjectType(DjangoObjectType):
    class Meta:
        model = SchoolType
        fields = ("id", "name")


class Query(graphene.ObjectType):
    school_types = graphene.List(SchoolTypeObjectType)
    school_type = graphene.Field(SchoolTypeObjectType, id=graphene.ID(required=True))

    def resolve_school_types(self, info: ResolveInfo) -> "QuerySet[SchoolType]":
        return SchoolType.objects.all()

    def resolve_school_type(self, info: ResolveInfo, id: int) -> Optional[SchoolType]:
        return get_obj_or_none(SchoolType, id)
