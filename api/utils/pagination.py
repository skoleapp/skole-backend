from typing import Union

import graphene
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from mypy.types import JsonDict

from core.models import Course, Resource, User


def get_paginator(
    qs: "QuerySet[Union[User, Course, Resource]]",
    page_size: int,
    page: int,
    paginated_type: graphene.ObjectType,
    **kwargs: JsonDict,
) -> graphene.ObjectType:

    p = Paginator(qs, page_size)

    try:
        page_obj = p.page(page)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    return paginated_type(
        page=page_obj.number,
        pages=p.num_pages,
        has_next=page_obj.has_next(),
        has_prev=page_obj.has_previous(),
        objects=page_obj.object_list,
        count=len(qs),  # FIXME: qs.count() throws an error for some reason.
        **kwargs,
    )


class PaginationMixin:
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    count = graphene.Int()
