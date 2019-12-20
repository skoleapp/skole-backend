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

    def resolve_subjects(self, info: ResolveInfo) -> List[Subject]:
        return Subject.objects.all()
