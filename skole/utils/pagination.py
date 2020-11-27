from typing import Type, TypeVar

import graphene
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import QuerySet

from skole.types import PaginableModel

T = TypeVar("T", bound=graphene.ObjectType)


def get_paginator(
    qs: QuerySet[PaginableModel], page_size: int, page: int, paginated_type: Type[T]
) -> T:

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
        count=qs.count(),
    )
