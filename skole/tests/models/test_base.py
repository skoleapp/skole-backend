import parler.managers
import parler.models
import pytest
from django.db import models

from skole.models import Badge, Comment, Thread
from skole.models.base import (
    SkoleManager,
    SkoleModel,
    TranslatableSkoleManager,
    TranslatableSkoleModel,
)


@pytest.mark.django_db
def test_repr() -> None:
    """Test `SkoleModel`'s `__repr__()`."""
    assert repr(Thread.objects.get(pk=1)) == "<Thread:1-test-thread-1>"
    assert repr(Comment.objects.get(pk=1)) == "<Comment:1-testuser2>"


def test_model_mro() -> None:
    """Test that the method resolution order of the base models make sense."""
    assert SkoleModel.__mro__ == (SkoleModel, models.Model, object)
    assert Comment.__mro__ == (Comment, SkoleModel, models.Model, object)

    assert TranslatableSkoleModel.__mro__ == (
        TranslatableSkoleModel,
        SkoleModel,
        parler.models.TranslatableModel,
        parler.models.TranslatableModelMixin,
        models.Model,
        object,
    )
    assert Badge.__mro__ == (
        Badge,
        TranslatableSkoleModel,
        SkoleModel,
        parler.models.TranslatableModel,
        parler.models.TranslatableModelMixin,
        models.Model,
        object,
    )


def test_manager_mro() -> None:
    """Test that the method resolution orders of the base managers make sense."""

    # We check these as strings, since `FromQuerySet` types are
    # dynamically created, and thus cannot be imported.
    assert [type_.__name__ for type_ in SkoleManager.__mro__] == [
        "SkoleManager",
        "Generic",
        "Manager",
        "BaseManagerFromQuerySet",
        "BaseManager",
        "object",
    ]
    assert [type_.__name__ for type_ in TranslatableSkoleManager.__mro__] == [
        "TranslatableSkoleManager",
        "SkoleManager",
        "Generic",
        "TranslatableManager",
        "ManagerFromTranslatableQuerySet",
        "Manager",
        "BaseManagerFromQuerySet",
        "BaseManager",
        "object",
    ]
