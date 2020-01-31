from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.schemas.school import SchoolObjectType
from api.utils.common import get_obj_or_none
from app.models import SchoolType


class SchoolTypeObjectType(DjangoObjectType):
    class Meta:
        model = SchoolType
        fields = ("id", "name")


class Query(graphene.ObjectType):
    school_types = graphene.List(SchoolTypeObjectType)
    school_type = graphene.Field(SchoolTypeObjectType, school_type_id=graphene.Int())

    def resolve_school_types(self, info: ResolveInfo) -> List[SchoolObjectType]:
        return SchoolType.objects.all()

    def resolve_school_type(
        self, info: ResolveInfo, school_type_id: int
    ) -> Optional[SchoolType]:
        return get_obj_or_none(SchoolType, school_type_id)
