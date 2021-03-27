from __future__ import annotations

from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import ExpressionWrapper, F, FloatField, QuerySet
from django.db.models.functions import Cast
from django.utils import timezone
from fcm_django.models import FCMDevice
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from skole.models.badge import Badge
from skole.models.badge_progress import BadgeProgress
from skole.models.base import SkoleManager, SkoleModel
from skole.models.referral_code import ReferralCode
from skole.utils.constants import Ranks, TokenAction, ValidationErrors, VerboseNames
from skole.utils.exceptions import ReferralCodeNeeded, UserAlreadyVerified
from skole.utils.token import get_token_payload
from skole.utils.validators import ValidateFileSizeAndType


class UserManager(SkoleManager["User"], BaseUserManager["User"]):
    def create_user(self, username: str, email: str, password: str) -> User:
        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
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

    def verify_user(self, token: str) -> User:
        payload = get_token_payload(
            token, TokenAction.VERIFICATION, settings.EXPIRATION_VERIFICATION_TOKEN
        )

        user = self.get(**payload)

        if not user.used_referral_code:
            raise ReferralCodeNeeded

        if user.verified is False:
            user.verified = True
            user.save()
            # We now have a fully activated user, let's give them their own referral code.
            ReferralCode.objects.create_referral_code(user)
            return user
        else:
            raise UserAlreadyVerified


class User(SkoleModel, AbstractBaseUser, PermissionsMixin):
    """Models one user on the platform."""

    slug = AutoSlugField(
        null=True,
        default=None,
        populate_from="username",
        unique=True,
        always_update=True,
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

    selected_badge_progress = models.ForeignKey(
        "skole.BadgeProgress",
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
    )

    used_referral_code = models.ForeignKey(
        "skole.ReferralCode",
        on_delete=models.PROTECT,
        related_name="referred_users",
        null=True,
    )

    score = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # Email notification permissions.
    comment_reply_email_permission = models.BooleanField(default=False)
    course_comment_email_permission = models.BooleanField(default=False)
    resource_comment_email_permission = models.BooleanField(default=False)
    new_badge_email_permission = models.BooleanField(default=False)

    # Push notification permissions.
    comment_reply_push_permission = models.BooleanField(default=True)
    course_comment_push_permission = models.BooleanField(default=True)
    resource_comment_push_permission = models.BooleanField(default=True)
    new_badge_push_permission = models.BooleanField(default=True)

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

    def change_score(self, score: int) -> None:
        if score:
            self.score += score  # Can also be a subtraction when `score` is negative.
            self.save(update_fields=("score",))

    def change_selected_badge_progress(self, badge: Badge) -> BadgeProgress:
        if not badge.pk:
            raise TypeError("Badge must have pk before it can be tracked.")
        badge_progress, __ = BadgeProgress.objects.get_or_create(badge=badge, user=self)
        self.selected_badge_progress = badge_progress
        self.save(update_fields=("selected_badge_progress",))
        return badge_progress

    def update_last_my_data_query(self) -> None:
        self.last_my_data_query = timezone.now()
        self.save()

    def get_or_create_badge_progresses(self) -> QuerySet[BadgeProgress]:
        """
        Create all the possibly missing BadgeProgress for the user and return them.

        Returns:
            QuerySet of BadgeProgress for all Badges that the User hasn't yet acquired.
            The result is sorted by the Badge's completion percentages.
        """
        missing = (
            Badge.objects.filter(steps__isnull=False)
            .exclude(badge_progresses__user=self)
            .values_list("pk", flat=True)
        )
        BadgeProgress.objects.bulk_create(
            (BadgeProgress(badge_id=pk, user=self) for pk in missing)
        )

        progresses = BadgeProgress.objects.filter(
            user=self, badge__steps__isnull=False, acquired__isnull=True
        )

        # `steps` is validated to be > 0 and non-null here, so the division is safe.
        return progresses.annotate(
            percentage=ExpressionWrapper(
                Cast("progress", FloatField()) / F("badge__steps"),
                output_field=FloatField(),
            ),
        ).order_by("-percentage")

    def register_fcm_token(self, token: str) -> None:
        FCMDevice.objects.get_or_create(user=self, registration_id=token)

    def get_acquired_badges(self) -> QuerySet[Badge]:
        """Return all the badges that the user has acquired."""
        return Badge.objects.filter(
            badge_progresses__user=self, badge_progresses__acquired__isnull=False
        )
