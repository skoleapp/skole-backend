import parler.managers
import parler.models
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone


class _SkoleManagerMixin:
    def get_queryset(self) -> "QuerySet[SkoleModel]":
        """Hide all soft deleted objects from queries."""

        # Ignore: Will be ok in subclasses.
        return super().get_queryset().exclude(deleted_at__isnull=False)  # type: ignore[misc]


# Ignore: Mypy expects Managers to have a generic type,
#  this doesn't actually work, so we ignore it.
#  https://gitter.im/mypy-django/Lobby?at=5de6bd09d75ad3721d4a58ba
class SkoleManager(_SkoleManagerMixin, models.Manager):  # type: ignore[type-arg]
    """Base manager for all non-translatable models."""


class TranslatableSkoleManager(_SkoleManagerMixin, parler.managers.TranslatableManager):
    """Base manager for all translatable models."""


class _SkoleModelMixin:
    """A mixin which adds soft deletion handling and other useful methods.

    This doesn't on purpose contain any fields because those need to defined in a class
    inheriting from Model for them to work.
    """

    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        # Ignore: Will be defined in subclasses.
        self.save()  # type: ignore[attr-defined]

    def __repr__(self) -> str:
        if hasattr(self, "name"):
            # Ignore: Mypy doesn't understand that the attribute has to exists now.
            name = f"-{self.name}"  # type: ignore[attr-defined]
        else:
            name = ""
        # Ignore: Will be defined in subclasses.
        return f"<{self.__class__.__name__}:{self.pk}{name}>"  # type: ignore[attr-defined]


class SkoleModel(_SkoleModelMixin, models.Model):
    """Base model for all non-translatable models."""

    # Ignore: Mypy thinks that the type of the variables should be datetime,
    #   since _SkoleModelMixin.delete sets its value to a datetime.
    deleted_at = models.DateTimeField(blank=True, null=True, default=None)  # type: ignore[assignment]

    class Meta:
        abstract = True

    objects = SkoleManager()


class TranslatableSkoleModel(_SkoleModelMixin, parler.models.TranslatableModel):
    """Base model for all translatable models.

    This inherits _SkoleModelMixin, instead of inheriting SkoleModel (which would then
    just inherit models.Model), to keep the method resolution order as
    `TranslatableSkoleModel -> _SkoleModelMixin -> TranslatableModel -> Model`, instead
    of `TranslatableSkoleModel -> SkoleModel -> Model -> TranslatableModel`.
    """

    # Ignore: See explanation in SkoleModel.
    deleted_at = models.DateTimeField(blank=True, null=True, default=None)  # type: ignore[assignment]

    class Meta:
        abstract = True

    objects = TranslatableSkoleManager()
