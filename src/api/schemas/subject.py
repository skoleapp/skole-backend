from typing import List

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from app.models import Subject


class SubjectType(DjangoObjectType):
    class Meta:
        model = Subject
        fields = ("id", "name", "schools")


class Query(graphene.ObjectType):
    subjects = graphene.List(SubjectType)
    subject = graphene.Field(SubjectType, id=graphene.Int())

    def resolve_subjects(self, info: ResolveInfo) -> List[Subject]:
        return Subject.objects.all()

    def resolve_subject(self, info: ResolveInfo, id: int) -> Subject:
        return Subject.objects.get(pk=id)
