from typing import List

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.schemas.user import UserTypePublic
from api.types.resource import ResourceType
from core.models import Course


class CourseType(DjangoObjectType):
    creator = graphene.Field(UserTypePublic)
    resources = graphene.List(ResourceType)

    class Meta:
        model = Course
        fields = ("id", "name", "code", "subject", "school", "creator", "modified", "created", "resources")


class Query(graphene.ObjectType):
    course_list = graphene.List(CourseType)
    course = graphene.Field(CourseType, id=graphene.Int())

    def resolve_course_list(self, info: ResolveInfo) -> List[Course]:
        return Course.objects.all()

    def resolve_course(self, info: ResolveInfo, id: int) -> Course:
        return Course.objects.get(pk=id)
