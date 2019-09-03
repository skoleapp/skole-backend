from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email: str, username: str, password: str) -> 'User':
        user = self.model(email=self.normalize_email(email),
                          username=username)

        user.is_staff = False
        user.is_superuser = False

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username: str, password: str) -> 'User':
        user = self.model(username=username)

        user.is_staff = True
        user.is_superuser = True

        user.set_password(password)
        user.save(using=self._db)

        return user

    @staticmethod
    def update_user(user: 'User', bio: str, email: str, title: str, username: str) -> 'User':
        """Update the user, used with PUT calls."""
        user.bio = bio
        user.email = email
        user.title = title
        user.username = username

        user.save()

        return user

    @staticmethod
    def set_password(user: 'User', password: str) -> 'User':
        user.set_password(password)
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Models one user on the platform."""
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(max_length=2000, null=True, blank=True)
    points = models.IntegerField(default=0)
    is_staff = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "username"

    def __str__(self) -> str:
        return f"{self.username}"

