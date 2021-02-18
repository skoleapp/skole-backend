import parler.managers
import parler.models
from django.db import models

from skole.models import Country, Course, Resource
from skole.models.base import (
    SkoleManager,
    SkoleModel,
    TranslatableSkoleManager,
    TranslatableSkoleModel,
)
from skole.types import Fixture


def test_repr(db: Fixture) -> None:
    """Test `SkoleModel`'s `__repr__()`."""
    assert (
        repr(Course.objects.get(pk=1))
        == "<Course:1-test-engineering-course-1-test0001>"
    )
    assert repr(Resource.objects.get(pk=1)) == "<Resource:1-sample-exam-1-2012-12-12>"


def test_model_mro() -> None:
    """Test that the method resolution order of the base models make sense."""
    assert SkoleModel.__mro__ == (SkoleModel, models.Model, object)
    assert Resource.__mro__ == (Resource, SkoleModel, models.Model, object)

    assert TranslatableSkoleModel.__mro__ == (
        TranslatableSkoleModel,
        SkoleModel,
        parler.models.TranslatableModel,
        parler.models.TranslatableModelMixin,
        models.Model,
        object,
    )
    assert Country.__mro__ == (
        Country,
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
