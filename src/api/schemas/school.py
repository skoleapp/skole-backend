from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.schemas.subject import SubjectObjectType
from api.utils.common import get_obj_or_none
from app.models import School


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

    def resolve_country(self, info: ResolveInfo) -> str:
        return self.city.country


class Query(graphene.ObjectType):
    schools = graphene.List(SchoolObjectType)
    school = graphene.Field(SchoolObjectType, school_id=graphene.Int())

    def resolve_schools(self, info: ResolveInfo) -> List[School]:
        return School.objects.order_by("name")

    def resolve_school(
        self, info: ResolveInfo, school_id: Optional[int] = None
    ) -> Optional[School]:
        return get_obj_or_none(School, school_id)
