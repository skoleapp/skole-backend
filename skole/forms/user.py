from typing import Any, Optional, Union, cast

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.files import File
from django.db.models import F, Q, QuerySet

from skole.forms.base import SkoleForm, SkoleModelForm
from skole.models import Badge, ReferralCode, User
from skole.models.attempted_email import AttemptedEmail
from skole.types import JsonDict
from skole.utils.constants import ValidationErrors
from skole.utils.files import clean_file_field


def get_all_users_except(user: User) -> QuerySet[User]:
    users = get_user_model().objects.all()
    if user.pk:
        return users.exclude(pk=user.pk)
    return users


class CleanUniqueEmailMixin:
    def clean_email(self) -> str:
        # Call `lower()` since we want all saved email to be lowercase.
        # Ignore: These attributes will exist in subclasses.
        email = self.cleaned_data["email"].lower()  # type: ignore[attr-defined]

        if "email" in self.changed_data:  # type: ignore[attr-defined]
            if email.split("@")[1] not in settings.ALLOWED_EMAIL_DOMAINS:
                attempt, __ = AttemptedEmail.objects.get_or_create(email=email)

                if not attempt.is_whitelisted:
                    raise forms.ValidationError(
                        ValidationErrors.EMAIL_DOMAIN_NOT_ALLOWED
                    )

                attempt.attempts = F("attempts") + 1
                attempt.save(update_fields=("attempts",))

            if (
                get_all_users_except(self.instance)  # type: ignore[attr-defined]
                .filter(Q(email__iexact=email) | Q(backup_email__iexact=email))
                .exists()
            ):
                raise forms.ValidationError(ValidationErrors.EMAIL_TAKEN)

        return email


class CleanUniqueUsernameMixin:
    def clean_username(self) -> str:
        # Ignore: These attributes will exist in subclasses.
        username = self.cleaned_data["username"]  # type: ignore[attr-defined]

        if "username" in self.changed_data:  # type: ignore[attr-defined]
            if get_all_users_except(self.instance).filter(username__iexact=username).exists():  # type: ignore[attr-defined]
                raise forms.ValidationError(ValidationErrors.USERNAME_TAKEN)

        return username


class RegisterForm(CleanUniqueUsernameMixin, CleanUniqueEmailMixin, SkoleModelForm):
    username = forms.CharField(min_length=settings.USERNAME_MIN_LENGTH)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password")

    def _post_clean(self) -> None:
        """Mimics the way Django's `UserCreationForm` does the password validation."""
        # Ignore: Mypy for some reason thinks that super doesn't define this method.
        super()._post_clean()  # type: ignore[misc]
        if password := self.cleaned_data.get("password"):
            # If form validation has failed, the password will not be in cleaned data.
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error("password", error)

    def save(self, commit: bool = True) -> User:
        return get_user_model().objects.create_user(**self.cleaned_data)


class TokenForm(SkoleForm):
    # We don't make the token required because we don't want
    # to return error messages for that specific field but rather
    # general error messages as the token is always a hidden field.
    token = forms.CharField(required=False)


class EmailForm(SkoleForm):
    email = forms.EmailField()


class LoginForm(SkoleModelForm):
    username_or_email = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = get_user_model()
        fields = ("username_or_email", "password")

    def clean(self) -> JsonDict:
        username_or_email = self.cleaned_data.get("username_or_email")
        password = self.cleaned_data.get("password")

        if "@" in username_or_email:
            query = Q(email__iexact=username_or_email) | Q(
                backup_email__iexact=username_or_email
            )
        else:
            query = Q(username__iexact=username_or_email)

        user: Optional[User]

        try:
            user = get_user_model().objects.get(query)
        except get_user_model().DoesNotExist:
            raise forms.ValidationError(ValidationErrors.AUTH_ERROR) from None
        else:
            if not user.is_active:
                raise forms.ValidationError(ValidationErrors.ACCOUNT_DEACTIVATED)
            if not user.used_referral_code:
                raise forms.ValidationError(
                    ValidationErrors.REFERRAL_CODE_NEEDED_BEFORE_LOGIN
                )

        user = cast(
            Optional[User], authenticate(username=user.username, password=password)
        )

        if not user:
            raise forms.ValidationError(ValidationErrors.AUTH_ERROR)

        if user.is_superuser:
            raise forms.ValidationError(ValidationErrors.SUPERUSER_LOGIN)

        self.cleaned_data["user"] = user
        return self.cleaned_data


class UpdateProfileForm(CleanUniqueUsernameMixin, SkoleModelForm):

    username = forms.CharField(min_length=settings.USERNAME_MIN_LENGTH)
    avatar = forms.CharField(required=False)

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "title",
            "bio",
            "avatar",
        )

    def clean_avatar(self) -> Union[File, str]:
        return clean_file_field(
            form=self, field_name="avatar", created_file_name="avatar"
        )


class UpdateAccountSettingsForm(CleanUniqueEmailMixin, SkoleModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "backup_email",
            "comment_reply_email_permission",
            "thread_comment_email_permission",
            "new_badge_email_permission",
            "comment_reply_push_permission",
            "thread_comment_push_permission",
            "new_badge_push_permission",
        )

    def clean_backup_email(self) -> str:
        backup_email = self.cleaned_data["backup_email"].lower()

        if backup_email:
            primary_email = self.cleaned_data.get("email") or self.instance.email

            if backup_email == primary_email:
                raise forms.ValidationError(
                    ValidationErrors.BACKUP_EMAIL_NOT_SAME_AS_EMAIL
                )

            if (
                get_all_users_except(self.instance)
                .filter(
                    Q(email__iexact=backup_email) | Q(backup_email__iexact=backup_email)
                )
                .exists()
            ):
                raise forms.ValidationError(ValidationErrors.EMAIL_TAKEN)

        return backup_email


class UpdateSelectedBadgeForm(SkoleModelForm):
    class Meta:
        model = Badge
        fields = ("id",)

    def save(self, commit: bool = True) -> Badge:
        # Prevent saving instance here - the mutation will just use this instance,
        # without actually ever mutating it.
        return self.instance


class ChangePasswordForm(SkoleModelForm):
    old_password = forms.CharField()

    class Meta:
        model = get_user_model()
        fields = ()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.fields["new_password"] = get_user_model().formfield("password")

    def clean_old_password(self) -> str:
        old_password = self.cleaned_data["old_password"]

        if not self.instance.check_password(old_password):
            raise forms.ValidationError(ValidationErrors.INVALID_OLD_PASSWORD)

        return old_password

    def clean_new_password(self) -> str:
        new_password = self.cleaned_data["new_password"]
        password_validation.validate_password(new_password, self.instance)
        return new_password


class SetPasswordForm(TokenForm):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.fields["new_password"] = get_user_model().formfield("password")


class DeleteUserForm(SkoleModelForm):
    class Meta:
        model = get_user_model()
        fields = ("password",)

    def clean_password(self) -> str:
        password = self.cleaned_data["password"]

        if not self.instance.check_password(password):
            raise forms.ValidationError(ValidationErrors.INVALID_PASSWORD)

        return password


class ReferralCodeForm(SkoleForm):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.fields["code"] = ReferralCode.formfield("code")
        self.fields["email"] = get_user_model().formfield("email")

    def clean_code(self) -> ReferralCode:
        code = self.cleaned_data["code"]
        referral_code = ReferralCode.objects.get_or_none(code=code)
        if not referral_code:
            raise forms.ValidationError(ValidationErrors.REFERRAL_CODE_INVALID)
        return referral_code

    def clean_email(self) -> str:
        email = self.cleaned_data["email"]
        user = get_user_model().objects.get_or_none(email__iexact=email)
        if not user:
            raise forms.ValidationError(ValidationErrors.EMAIL_DOES_NOT_EXIST)
        self.cleaned_data["user"] = user
        return email
