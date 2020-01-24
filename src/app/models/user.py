from typing import Any

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class UserManager(BaseUserManager):
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

    def update_user(self, user: "User", **kwargs: Any) -> "User":
        for key, value in kwargs.items():
            if key in {"bio", "title"} and value == "":
                # Avoid having empty strings in the db.
                value = None
            setattr(user, key, value)

        user.save()
        return user

    @staticmethod
    def set_password(user: "User", password: str) -> "User":
        user.set_password(password)

        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Models one user on the platform."""

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(max_length=2000, null=True, blank=True)
    avatar = models.ImageField(upload_to="uploads/avatars", null=True, blank=True)
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
