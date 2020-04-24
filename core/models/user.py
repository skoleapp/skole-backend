from typing import Union

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from core.utils.validators import ValidateFileSizeAndType
from core.utils.vote import (
    SCORE_COMMENT_MULTIPLIER,
    SCORE_COURSE_MULTIPLIER,
    SCORE_RESOURCE_MULTIPLIER,
)


# Ignore: Mypy expects Managers to have a generic type,
#  this doesn't actually work, so we ignore it.
#  https://gitter.im/mypy-django/Lobby?at=5de6bd09d75ad3721d4a58ba
class UserManager(BaseUserManager):  # type: ignore[type-arg]
    def create_user(self, username: str, email: str, password: str) -> "User":
        user = self.model(username=username, email=self.normalize_email(email))
        user.avatar = None
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username: str, email: str, password: str) -> "User":
        user = self.model(username=username, email=self.normalize_email(email))
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
        user.email = self.normalize_email(email)
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

    @staticmethod
    def change_score(user: "User", score: int) -> "User":
        user.score += score  # Can also be a subtraction when `score` is negative.
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Models one user on the platform."""

    username = models.CharField(
        max_length=30,
        unique=True,
        error_messages={"unique": _("This username is taken.")},
    )
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
    score = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)
    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    def __str__(self) -> str:
        return f"{self.username}"
