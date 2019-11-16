from typing import List

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from app.models.subject import Subject


class SubjectType(DjangoObjectType):
    class Meta:
        model = Subject
        fields = ("id", "name")


class Query(graphene.ObjectType):
    subjects = graphene.List(SubjectType, school_id=graphene.String())

    def resolve_subjects(self, info: ResolveInfo, school_id: str = None) -> List[Subject]:
        if school_id is not None:
            return Subject.objects.filter(schools__pk=school_id)
        else:
            return Subject.objects.all()
