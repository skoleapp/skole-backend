from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.schemas.subject import SubjectObjectType
from api.utils.common import get_obj_or_none
from core.models import School


class SchoolObjectType(DjangoObjectType):
    school_type = graphene.String()
    city = graphene.String()
    country = graphene.String()
    subjects = graphene.List(SubjectObjectType)
    subject_count = graphene.Int()
    course_count = graphene.Int()

    class Meta:
        model = School
        fields = ("id", "name", "subjects", "courses", "subject_count", "course_count")

    @login_required
    def resolve_country(self, info: ResolveInfo) -> str:
        return self.city.country


class Query(graphene.ObjectType):
    schools = graphene.List(SchoolObjectType)
    school = graphene.Field(SchoolObjectType, id=graphene.ID())

    @login_required
    def resolve_schools(self, info: ResolveInfo) -> "QuerySet[School]":
        return School.objects.order_by("name")

    @login_required
    def resolve_school(
        self, info: ResolveInfo, id: Optional[int] = None
    ) -> Optional[School]:
        return get_obj_or_none(School, id)
