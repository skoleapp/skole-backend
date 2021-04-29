from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

from django.db.models import Case, IntegerField, Model, Q, QuerySet, Value, When

from skole.types import FormError

T = TypeVar("T")
M = TypeVar("M", bound=Model)
E = TypeVar("E", bound=FormError)


def full_refresh_from_db(instance: M, /) -> M:
    """
    Return the same object instance but re-query it from the database.

    This is like Django's `refresh_from_db,` but this also recalculates the values of
    `get_queryset` annotations and aggregations.
    """
    return instance.__class__.objects.get(pk=instance.pk)


def join_queries(
    model: type[M], *expressions: Q, order_by: Iterable[str] = ()
) -> QuerySet[M]:
    """
    Join queries while preserving their individual order.

    If one would want to join the queries:
    `Foo.objects.filter(name="foo")` and `Foo.objects.filter(name="bar")` so that the
    objects from the first query would be at the start of the queryset and the objects
    from the second query would at the end of the queryset, one could use:
    `join_querysets(Foo, Q(name="foo"), Q(name="bar"))`

    References:
        https://stackoverflow.com/q/38583295/9835872
    """
    if isinstance(order_by, str):
        raise TypeError(
            "`order_by` should be an iterable of strings, and not a string."
        )

    def values_pk(expr: Q) -> QuerySet[M]:
        return model.objects.filter(expr).values("pk")

    when_cases = (
        When(pk__in=values_pk(expr), then=Value(i))
        for i, expr in enumerate(expressions)
    )

    return (
        model.objects.annotate(
            grouped_ordering=Case(
                *when_cases,
                output_field=IntegerField(),
            ),
        )
        .exclude(grouped_ordering__isnull=True)
        .order_by("grouped_ordering", *order_by)
    )


def to_form_error(value: str) -> FormError:
    """Use to add the GraphQL mutation form error structure to an error message."""
    return [{"field": "__all__", "messages": [value]}]
