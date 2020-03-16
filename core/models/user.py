from typing import Union

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.db.models import Sum
from django.db.models.query import QuerySet
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from core.utils.validators import ValidateFileSizeAndType
from core.utils.vote import (
    POINTS_COMMENT_MULTIPLIER,
    POINTS_COURSE_MULTIPLIER,
    POINTS_RESOURCE_MULTIPLIER,
)


# Ignore: Mypy expects Managers to have a generic type,
#  this doesn't actually work, so we ignore it.
#  https://gitter.im/mypy-django/Lobby?at=5de6bd09d75ad3721d4a58ba
class UserManager(BaseUserManager):  # type: ignore[type-arg]
    def create_user(self, email: str, username: str, password: str) -> "User":
        user = self.model(email=self.normalize_email(email), username=username)

        user.is_staff = False
        user.is_superuser = False

        user.avatar = None
        user.set_password(password)

        user.save()
        return user

    def create_superuser(self, email: str, username: str, password: str) -> "User":
        user = self.model(email=email, username=username)
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)

        user.save()
        return user

    def update_user(
        self,
        user: "User",
        username: str,
        email: str,
        title: str,
        bio: str,
        avatar: Union[UploadedFile, str],
    ) -> "User":
        user.username = username
        user.email = email
        user.title = title
        user.bio = bio
        user.avatar = avatar

        user.save()
        return user

    @staticmethod
    def set_password(user: "User", password: str) -> "User":
        user.set_password(password)

        user.save()
        return user

    def get_queryset(self) -> "QuerySet[User]":
        return (
            super()
            .get_queryset()
            .annotate(
                points=Sum("created_courses__votes__status") * POINTS_COURSE_MULTIPLIER
                + Sum("created_resources__votes__status") * POINTS_RESOURCE_MULTIPLIER
                + Sum("comments__votes__status") * POINTS_COMMENT_MULTIPLIER
            )
        )


class User(AbstractBaseUser, PermissionsMixin):
    """Models one user on the platform."""

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=2000, blank=True)
    avatar = models.ImageField(
        upload_to="uploads/avatars",
        blank=True,
        validators=[ValidateFileSizeAndType(2, ["image/jpeg", "image/png"])],
    )
    avatar_thumbnail = ImageSpecField(
        source="avatar",
        processors=[ResizeToFill(100, 100)],
        format="JPEG",
        options={"quality": 60},
    )

    is_staff = models.BooleanField(default=False)

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return f"{self.username}"
