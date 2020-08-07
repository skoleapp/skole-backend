import time
from typing import Any, List, Optional, Union

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import UploadedFile
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from graphql import ResolveInfo
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from mypy.types import JsonDict

from skole.models.base import SkoleManager, SkoleModel
from skole.models.school import School
from skole.models.subject import Subject
from skole.utils.constants import Ranks, TokenAction, ValidationErrors
from skole.utils.exceptions import UserAlreadyVerified, UserNotVerified
from skole.utils.token import get_token, get_token_payload
from skole.utils.validators import ValidateFileSizeAndType


# Ignore: See explanation in SkoleManager.
class UserManager(SkoleManager, BaseUserManager):  # type: ignore[type-arg]
    def create_user(
        self,
        username: str,
        email: str,
        school: Optional[School],
        subject: Optional[Subject],
        password: str,
    ) -> "User":
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            school=school,
            subject=subject,
        )

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
        school: Optional[School],
        subject: Optional[Subject],
    ) -> "User":
        user.username = username
        user.email = self.normalize_email(email)
        user.title = title
        user.bio = bio
        user.avatar = avatar
        user.school = school
        user.subject = subject
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

    def verify_user(self, token: str) -> "User":
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

    username = models.CharField(
        max_length=30,
        unique=True,
        error_messages={"unique": ValidationErrors.USERNAME_TAKEN},
        validators=[
            RegexValidator(settings.USERNAME_REGEX, ValidationErrors.INVALID_USERNAME)
        ],
    )

    email = models.EmailField(
        unique=True, error_messages={"unique": ValidationErrors.EMAIL_TAKEN},
    )

    title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=2000, blank=True)

    avatar = models.ImageField(
        upload_to="uploads/avatars",
        validators=[
            ValidateFileSizeAndType(2, [("image/jpeg", "JPEG"), ("image/png", "PNG")])
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

    # Ignore: Mypy somehow thinks that this is incompatible with the super class.
    objects = UserManager()  # type: ignore[assignment]

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = [EMAIL_FIELD]

    def __str__(self) -> str:
        return f"{self.username}"

    def send(
        self,
        subject: str,
        template: str,
        context: JsonDict,
        recipient_list: Optional[List[str]] = None,
    ) -> None:
        subject = render_to_string(subject, context).replace("\n", " ").strip()
        html_message = render_to_string(template, context)
        message = strip_tags(html_message)

        send_mail(
            subject=subject,
            from_email=settings.EMAIL_AUTH_FROM,
            message=message,
            html_message=html_message,
            recipient_list=(recipient_list or [self.email]),
            fail_silently=False,
        )

    def get_email_context(
        self, info: ResolveInfo, path: str, action: str, **kwargs: JsonDict
    ) -> JsonDict:
        assert info.context is not None
        token = get_token(self, action, **kwargs)
        site = get_current_site(info.context)

        return {
            "user": self,
            "request": info.context,
            "token": token,
            "port": info.context.get_port(),
            "site_name": site.name,
            "domain": site.domain,
            "protocol": "http" if settings.DEBUG else "https",
            "path": path,
            "timestamp": time.time(),
        }

    def send_verification_email(
        self, info: ResolveInfo, *args: Any, **kwargs: Any
    ) -> None:
        email_context = self.get_email_context(
            info, settings.VERIFICATION_PATH_ON_EMAIL, TokenAction.VERIFICATION
        )

        subject = settings.EMAIL_SUBJECT_VERIFICATION
        template = settings.EMAIL_TEMPLATE_VERIFICATION
        return self.send(subject, template, email_context, *args, **kwargs)

    def resend_verification_email(
        self, info: ResolveInfo, *args: Any, **kwargs: Any
    ) -> None:
        if self.verified is True:
            raise UserAlreadyVerified

        email_context = self.get_email_context(
            info, settings.VERIFICATION_PATH_ON_EMAIL, TokenAction.VERIFICATION
        )

        subject = settings.EMAIL_SUBJECT_VERIFICATION
        template = settings.EMAIL_TEMPLATE_VERIFICATION
        return self.send(subject, template, email_context, *args, **kwargs)

    def send_password_reset_email(
        self, info: ResolveInfo, *args: Any, **kwargs: Any
    ) -> None:
        if self.verified is False:
            raise UserNotVerified

        email_context = self.get_email_context(
            info, settings.PASSWORD_RESET_PATH_ON_EMAIL, TokenAction.PASSWORD_RESET
        )

        template = settings.EMAIL_TEMPLATE_PASSWORD_RESET
        subject = settings.EMAIL_SUBJECT_PASSWORD_RESET
        return self.send(subject, template, email_context, *args, **kwargs)

    @property
    def rank(self) -> str:
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
