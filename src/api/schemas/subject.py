from typing import List, Optional

import graphene
from graphene_django import DjangoObjectType
from graphql import ResolveInfo
from app.models import Subject


class SubjectType(DjangoObjectType):
    class Meta:
        model = Subject
        fields = ("id", "name", "schools")


class Query(graphene.ObjectType):
    subjects = graphene.List(SubjectType, school_id=graphene.String())
    subject = graphene.Field(SubjectType, subject_id=graphene.Int())

    def resolve_subjects(self, info: ResolveInfo, school_id: Optional[str] = None) -> List[Subject]:
        if school_id is not None:
            return Subject.objects.filter(schools__pk=school_id)
        else:
            return Subject.objects.all()

    def resolve_subject(self, info: ResolveInfo, subject_id: Optional[int] = None) -> Optional[Subject]:
        if subject_id is not None:
            return Subject.objects.get(pk=subject_id)
        else:
            return None
