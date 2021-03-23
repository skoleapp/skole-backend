from typing import Any, Optional, Union, cast

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.files import File

from skole.models import Badge, User
from skole.types import JsonDict
from skole.utils.constants import ValidationErrors
from skole.utils.files import clean_file_field

from .base import SkoleForm, SkoleModelForm


class RegisterForm(SkoleModelForm):
    username = forms.CharField(min_length=settings.USERNAME_MIN_LENGTH)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password")

    def clean_username(self) -> str:
        username = self.cleaned_data["username"]
        if get_user_model().objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(ValidationErrors.USERNAME_TAKEN)
        return username

    def clean_email(self) -> str:
        # Call `lower()` since we want all saved email to be lowercase.
        email = self.cleaned_data["email"].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(ValidationErrors.EMAIL_TAKEN)
        return email

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
            query = {"email__iexact": username_or_email}
        else:
            query = {"username__iexact": username_or_email}

        user: Optional[User]

        try:
            user = get_user_model().objects.get(**query)
            if not user.is_active:
                raise forms.ValidationError(ValidationErrors.ACCOUNT_DEACTIVATED)
        except get_user_model().DoesNotExist:
            raise forms.ValidationError(ValidationErrors.AUTH_ERROR) from None

        user = cast(
            Optional[User], authenticate(username=user.username, password=password)
        )

        if not user:
            raise forms.ValidationError(ValidationErrors.AUTH_ERROR)

        if user.is_superuser:
            raise forms.ValidationError(ValidationErrors.SUPERUSER_LOGIN)

        self.cleaned_data["user"] = user
        return self.cleaned_data


class UpdateProfileForm(SkoleModelForm):

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

    def clean_username(self) -> str:
        username = self.cleaned_data["username"]
        if "username" in self.changed_data:
            if get_user_model().objects.filter(username__iexact=username):
                raise forms.ValidationError(ValidationErrors.USERNAME_TAKEN)
        return username


class UpdateAccountSettingsForm(SkoleModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "school",
            "subject",
            "product_update_email_permission",
            "blog_post_email_permission",
            "comment_reply_email_permission",
            "course_comment_email_permission",
            "resource_comment_email_permission",
            "new_badge_email_permission",
            "comment_reply_push_permission",
            "course_comment_push_permission",
            "resource_comment_push_permission",
            "new_badge_push_permission",
        )

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].lower()
        if "email" in self.changed_data:
            if get_user_model().objects.filter(email__iexact=email):
                raise forms.ValidationError(ValidationErrors.EMAIL_TAKEN)

        return email


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
