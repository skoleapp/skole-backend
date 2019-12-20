from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from app.models import Subject


class SubjectType(DjangoObjectType):
    class Meta:
        model = Subject
        fields = ("id", "name")


class Query(graphene.ObjectType):
    subjects = graphene.List(SubjectType)
    subject = graphene.Field(SubjectType, subject_id=graphene.Int())

    def resolve_subjects(self, info: ResolveInfo) -> List[Subject]:
        return Subject.objects.all()

    def resolve_subject(self, info: ResolveInfo, subject_id: Optional[int] = None) -> Optional[Subject]:
        return Subject.objects.get(pk=subject_id)
