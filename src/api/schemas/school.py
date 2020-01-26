from api.schemas.subject import SubjectObjectType
from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

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
        try:
            return School.objects.get(pk=school_id)
        except School.DoesNotExist:
            # Return None instead of throwing a GraphQL Error.
            return None
