from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.utils.common import get_obj_or_none
from core.models import SchoolType


class SchoolTypeObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = SchoolType
        fields = ("id", "name")


class Query(graphene.ObjectType):
    school_types = graphene.List(SchoolTypeObjectType)
    school_type = graphene.Field(SchoolTypeObjectType, id=graphene.ID())

    @login_required
    def resolve_school_types(self, info: ResolveInfo) -> "QuerySet[SchoolType]":
        return SchoolType.objects.all()

    @login_required
    def resolve_school_type(
        self, info: ResolveInfo, id: Optional[int] = None
    ) -> Optional[SchoolType]:
        return get_obj_or_none(SchoolType, id)
