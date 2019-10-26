from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from core.utils import ENGLISH, LANGUAGES


class UserManager(BaseUserManager):
    def create_user(self, email: str, username: str, password: str) -> "User":
        user = self.model(email=self.normalize_email(email), username=username)

        user.is_staff = False
        user.is_superuser = False

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

    @staticmethod
    def update_user(user: 'User', **kwargs) -> 'User':
        for key, value in kwargs.items():
            setattr(user, key, value)

        user.save()
        return user

    @staticmethod
    def set_password(user: 'User', password: str) -> "User":
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Models one user on the platform."""

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(max_length=2000, null=True, blank=True)
    language = models.CharField(choices=LANGUAGES, default=ENGLISH, max_length=7)
    points = models.IntegerField(default=0)
    is_staff = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return f"{self.username}"
