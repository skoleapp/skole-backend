from __future__ import annotations

from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from skole.models.base import SkoleManager, SkoleModel
from skole.utils.validators import ValidateFileSizeAndType


class ThreadManager(SkoleManager["Thread"]):
    def get_queryset(self) -> QuerySet[Thread]:
        qs = super().get_queryset()

        return qs.annotate(
            star_count=Count("stars", distinct=True),
            comment_count=Count("comments", distinct=True)
            + Count("comments__reply_comments", distinct=True),
        )


class Thread(SkoleModel):
    """Models one thread."""

    title = models.CharField(max_length=200)
    text = models.TextField(max_length=10000, blank=True)

    slug = AutoSlugField(
        null=True,
        default=None,
        populate_from="__str__",
        unique=True,
    )

    image = models.ImageField(
        # Keep this path consistent with `Comment.image`.
        # It cannot be changed yet, see the comment on it for more details.
        upload_to="uploads/attachments",
        blank=True,
        validators=[
            ValidateFileSizeAndType(
                settings.IMAGE_MAX_SIZE,
                settings.IMAGE_ALLOWED_FILETYPES,
            )
        ],
    )

    image_thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(100, 100)],
        format="JPEG",
        options={"quality": 60},
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_threads",
    )

    score = models.IntegerField(default=0)

    views = models.PositiveIntegerField(default=0)

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    # These values will get annotated in the manager's get_queryset.
    star_count: int
    comment_count: int

    def __str__(self) -> str:
        return f"{self.title}"

    def change_score(self, score: int) -> None:
        if score:
            self.score += score  # Can also be a subtraction when `score` is negative.
            self.save(update_fields=("score",))

    def increment_views(self, request: HttpRequest) -> None:
        if request.user != self.user:
            # Using `F("views")` + 1 errors in the GraphQL resolver somehow.
            self.views += 1
            self.save(update_fields=("views",))
