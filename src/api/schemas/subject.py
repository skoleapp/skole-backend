from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from api.utils.common import get_obj_or_none
from app.models import Subject


class SubjectObjectType(DjangoObjectType):
    class Meta:
        model = Subject
        fields = ("id", "name")


class Query(graphene.ObjectType):
    subjects = graphene.List(SubjectObjectType)
    subject = graphene.Field(SubjectObjectType, id=graphene.ID(required=True))

    def resolve_subjects(self, info: ResolveInfo) -> "QuerySet[Subject]":
        return Subject.objects.order_by("name")

    def resolve_subject(self, info: ResolveInfo, id: int) -> Optional[Subject]:
        return get_obj_or_none(Subject, id)
