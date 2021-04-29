from __future__ import annotations

from typing import Any, ClassVar, Generic, TypeVar, cast, get_args

from django.db.models.signals import post_save
from django.dispatch import Signal

from skole.models import Badge, Comment, SkoleModel, Thread, User, Vote
from skole.models.badge_progress import BadgeProgress

T = TypeVar("T", bound="BadgeSignalHandlerMeta")
M = TypeVar("M", bound=SkoleModel)


class BadgeSignalHandlerMeta(type):
    def __new__(
        mcs: type[T], name: str, bases: tuple[type, ...], attrs: dict[str, Any]
    ) -> T:
        cls = cast(T, super().__new__(mcs, name, bases, attrs))

        if name != "BadgeSignalHandler":
            msg = "Subclasses of `BadgeSignalHandler` must "

            for attr in BadgeSignalHandler.__annotations__:
                if not hasattr(cls, attr):
                    raise TypeError(msg + f"define the `{attr}` class attribute.")
            if "get_current_progress" not in attrs:
                raise TypeError(
                    msg + "implement the `get_current_progress` static method."
                )

            # Ignore: Type checking should make sure that the derived classes have this
            #   generic parameter.
            sender = get_args(cls.__orig_bases__[0])[0]  # type: ignore[attr-defined]

            # Ignore: We just checked that these attributes did exist on `cls`.
            cls.signal.connect(cls.update_progress, sender=sender)  # type: ignore[attr-defined]

        return cls


class BadgeSignalHandler(Generic[M], metaclass=BadgeSignalHandlerMeta):
    """
    Base class for signal handlers which update a certain Badge's progress for users.

    Attributes:
        identifier: The `Badge.identifier` that specifies the Badge object whom
            progress this tracks, e.g `"first_comment"`.
        signal: A valid Django Signal, e.g. `post_save`.

    Methods:
        get_current_progress: Implement this as a method which returns the current
            value for a user's `BadgeProgress.progress` as an integer.
    """

    identifier: ClassVar[str]
    signal: ClassVar[Signal] = post_save

    @staticmethod
    def get_current_progress(user: User) -> int:
        ...

    def __init__(self) -> None:
        raise TypeError("You shouldn't need to initialize this class.")

    @classmethod
    def update_progress(
        cls,
        sender: type[M],
        instance: M,
        created: bool,
        raw: bool,
        **kwargs: Any,
    ) -> None:
        if not hasattr(instance, "user"):
            raise TypeError(
                f"Cannot use this default implementation to update progress, "
                f"since {type(instance)} doesn't have a `user` attribute."
            )

        # Ignore: We know that `instance` must have the `user` attribute now.
        user = instance.user  # type: ignore[attr-defined]

        if not created or raw or not user:
            return

        badge_id = (
            Badge.objects.filter(identifier=cls.identifier)
            .values_list("pk", flat=True)
            .get()
        )

        badge_progress, __ = BadgeProgress.objects.get_or_create(
            badge_id=badge_id, user=user
        )
        assert badge_progress.badge.steps is not None

        if (progress := cls.get_current_progress(user)) != badge_progress.progress:
            badge_progress.progress = progress
            badge_progress.save(update_fields=("progress",))


class FirstCommentBadgeSignalHandler(BadgeSignalHandler[Comment]):
    identifier = "first_comment"

    @staticmethod
    def get_current_progress(user: User) -> int:
        return user.comments.count()


class FirstThreadBadgeSignalHandler(BadgeSignalHandler[Thread]):
    identifier = "first_thread"

    @staticmethod
    def get_current_progress(user: User) -> int:
        return user.created_threads.count()


class FirstUpvoteBadgeSignalHandler(BadgeSignalHandler[Vote]):
    identifier = "first_upvote"

    @staticmethod
    def get_current_progress(user: User) -> int:
        return user.votes.filter(status=1).count()


class FirstDownvoteBadgeSignalHandler(BadgeSignalHandler[Vote]):
    identifier = "first_downvote"

    @staticmethod
    def get_current_progress(user: User) -> int:
        return user.votes.filter(status=-1).count()
