from typing import Union

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


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

    def get_queryset(self):
        return super().get_queryset().filter(is_superuser=False)


class User(AbstractBaseUser, PermissionsMixin):  # type: ignore[misc]
    """Models one user on the platform."""

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=2000, blank=True)
    avatar = models.ImageField(upload_to="uploads/avatars", blank=True)
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
