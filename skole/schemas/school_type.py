from typing import Optional

import graphene
from django.db.models import QuerySet

from skole.models import SchoolType
from skole.schemas.base import SkoleDjangoObjectType, SkoleObjectType
from skole.types import ResolveInfo


class SchoolTypeObjectType(SkoleDjangoObjectType):
    slug = graphene.String()
    name = graphene.String()

    class Meta:
        model = SchoolType
        fields = ("slug", "name")


class Query(SkoleObjectType):
    autocomplete_school_types = graphene.List(SchoolTypeObjectType)
    school_type = graphene.Field(SchoolTypeObjectType, slug=graphene.String())

    @staticmethod
    def resolve_autocomplete_school_types(
        root: None, info: ResolveInfo
    ) -> QuerySet[SchoolType]:
        """Results are sorted by creation time."""
        return SchoolType.objects.order_by("pk")

    @staticmethod
    def resolve_school_type(
        root: None, info: ResolveInfo, slug: str = ""
    ) -> Optional[SchoolType]:
        return SchoolType.objects.get_or_none(slug=slug)
