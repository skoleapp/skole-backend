from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar

import parler.managers
import parler.models
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

M = TypeVar("M", bound="SkoleModel", covariant=True)
TM = TypeVar("TM", bound="TranslatableSkoleModel", covariant=True)


class SkoleManager(Generic[M], models.Manager[M]):
    """Base manager for all non-translatable models."""

    def get_queryset(self) -> QuerySet[M]:
        """Hide all soft deleted objects from queries."""
        return super().get_queryset().exclude(deleted_at__isnull=False).order_by("pk")

    def get_or_none(self, *args: Any, **kwargs: Any) -> Optional[M]:
        """
        Return the object queried with `args` and `kwargs` or None if it didn't exist.

        Raises:
            MultipleObjectsReturned: If the query matches multiple objects.
        """
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None


class TranslatableSkoleManager(SkoleManager[TM], parler.managers.TranslatableManager):
    """Base manager for all translatable models."""


class SkoleModel(models.Model):
    """Base model for all non-translatable models."""

    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        self.save()

    def __repr__(self) -> str:
        if hasattr(self, "name"):
            # Ignore: Mypy doesn't understand that the attribute has to exists now.
            name = f"-{self.name}"  # type: ignore[attr-defined]
        else:
            name = ""
        return f"<{self.__class__.__name__}:{self.pk}{name}>"

    deleted_at = models.DateTimeField(blank=True, null=True, default=None)

    class Meta:
        abstract = True

    objects = SkoleManager()


class TranslatableSkoleModel(SkoleModel, parler.models.TranslatableModel):
    """Base model for all translatable models."""

    class Meta:
        abstract = True

    objects = TranslatableSkoleManager()
