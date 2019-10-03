from datetime import datetime, timedelta

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from rest_framework.authtoken.models import Token

from core.utils import ENGLISH, LANGUAGES


class UserManager(BaseUserManager):
    def create_user(self, email: str, username: str, password: str) -> "User":
        user = self.model(email=self.normalize_email(email), username=username)

        user.is_staff = False
        user.is_superuser = False

        user.set_password(password)

        user.save()
        return user

    def create_superuser(self, username: str, password: str) -> "User":
        user = self.model(username=username)

        user.is_staff = True
        user.is_superuser = True

        user.set_password(password)

        user.save()
        return user

    @staticmethod
    def set_password(user: 'User', password: str) -> "User":
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def set_language(user: 'User', language: str) -> "User":
        user.language = language
        user.save()
        return user

    @staticmethod
    def refresh_token(user: 'User', token: Token) -> Token:
        utc_now = datetime.utcnow()
        if token.created.replace(tzinfo=None) < utc_now - timedelta(hours=24):
            token.delete()
            refresh_token = Token.objects.create(user=user)
            refresh_token.created = datetime.utcnow()
            refresh_token.save()
            return refresh_token

        return token


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

    USERNAME_FIELD = "username"

    def __str__(self) -> str:
        return f"{self.username}"
