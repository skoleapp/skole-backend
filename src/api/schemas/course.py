from typing import List

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.schemas.user import UserTypePublic
from api.types.resource import ResourceType
from app.models import Course


class CourseType(DjangoObjectType):
    creator = graphene.Field(UserTypePublic)
    resources = graphene.List(ResourceType)

    class Meta:
        model = Course
        fields = ("id", "name", "code", "subject", "school", "creator", "modified", "created", "resources")


class Query(graphene.ObjectType):
    courses = graphene.List(CourseType, subject_id=graphene.Int())
    course = graphene.Field(CourseType, id=graphene.Int())

    def resolve_courses(self, info: ResolveInfo, subject_id: int = None) -> List[Course]:
        if subject_id is not None:
            return Course.objects.filter(subject__pk=subject_id)
        else:
            return Course.objects.all()

    def resolve_course(self, info: ResolveInfo, id: int) -> Course:
        return Course.objects.get(pk=id)
