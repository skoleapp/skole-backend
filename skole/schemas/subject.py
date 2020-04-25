from typing import Optional

import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from skole.models import Subject
from skole.utils.shortcuts import get_obj_or_none


class SubjectObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = Subject
        fields = ("id", "name")


class Query(graphene.ObjectType):
    subjects = graphene.List(SubjectObjectType)
    subject = graphene.Field(SubjectObjectType, id=graphene.ID())

    @login_required
    def resolve_subjects(self, info: ResolveInfo) -> "QuerySet[Subject]":
        assert info.context is not None
        return Subject.objects.translated(info.context.LANGUAGE_CODE).order_by(
            "translations__name"
        )

    @login_required
    def resolve_subject(
        self, info: ResolveInfo, id: Optional[int] = None
    ) -> Optional[Subject]:
        return get_obj_or_none(Subject, id)
