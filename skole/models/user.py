from __future__ import annotations

from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from skole.utils.constants import Ranks, TokenAction, ValidationErrors, VerboseNames
from skole.utils.exceptions import UserAlreadyVerified
from skole.utils.token import get_token_payload
from skole.utils.validators import ValidateFileSizeAndType

from .base import SkoleManager, SkoleModel


class UserManager(SkoleManager["User"], BaseUserManager["User"]):
    def create_user(self, username: str, email: str, password: str) -> User:
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username: str, email: str, password: str) -> User:
        user = self.model(username=username, email=self.normalize_email(email))
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def set_password(user: User, password: str) -> User:
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def change_score(user: User, score: int) -> User:
        user.score += score  # Can also be a subtraction when `score` is negative.
        user.save()
        return user

    def verify_user(self, token: str) -> User:
        payload = get_token_payload(
            token, TokenAction.VERIFICATION, settings.EXPIRATION_VERIFICATION_TOKEN
        )

        user = self.get(**payload)

        if user.verified is False:
            user.verified = True
            user.save()
            return user
        else:
            raise UserAlreadyVerified


class User(SkoleModel, AbstractBaseUser, PermissionsMixin):
    """Models one user on the platform."""

    _identifier_field = "username"

    slug = AutoSlugField(
        null=True, default=None, populate_from="username", always_update=True
    )

    username = models.CharField(
        VerboseNames.USERNAME,
        max_length=30,
        unique=True,
        error_messages={"unique": ValidationErrors.USERNAME_TAKEN},
        validators=[
            RegexValidator(settings.USERNAME_REGEX, ValidationErrors.INVALID_USERNAME)
        ],
    )

    email = models.EmailField(
        VerboseNames.EMAIL,
        unique=True,
        error_messages={"unique": ValidationErrors.EMAIL_TAKEN},
    )

    title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=2000, blank=True)

    avatar = models.ImageField(
        upload_to="uploads/avatars",
        validators=[
            ValidateFileSizeAndType(
                settings.USER_AVATAR_MAX_SIZE, settings.USER_AVATAR_ALLOWED_FILETYPES
            )
        ],
        blank=True,
        default=None,
    )

    avatar_thumbnail = ImageSpecField(
        source="avatar",
        processors=[ResizeToFill(100, 100)],
        format="JPEG",
        options={"quality": 60},
    )

    school = models.ForeignKey(
        "skole.School",
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
    )

    subject = models.ForeignKey(
        "skole.Subject",
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
    )

    score = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)

    last_my_data_query = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The time when the user last used the GDPR `myData` query.",
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = [EMAIL_FIELD]

    def __str__(self) -> str:
        return f"{self.username}"

    @property
    def rank(self) -> str:  # pylint: disable=too-many-return-statements
        if self.score < 100:
            return Ranks.FRESHMAN
        elif self.score < 250:
            return Ranks.TUTOR
        elif self.score < 500:
            return Ranks.MENTOR
        elif self.score < 1000:
            return Ranks.BACHELOR
        elif self.score < 2000:
            return Ranks.MASTER
        elif self.score < 5000:
            return Ranks.DOCTOR
        else:
            return Ranks.PROFESSOR

    def update_last_my_data_query(self) -> None:
        self.last_my_data_query = timezone.now()
        self.save()
