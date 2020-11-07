from typing import Optional, Union, cast

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.files import File

from skole.models import User
from skole.types import JsonDict
from skole.utils.constants import FieldOperation, ValidationErrors
from skole.utils.files import clean_file_field, clean_metadata

from .base import SkoleForm, SkoleModelForm


class RegisterForm(SkoleModelForm):
    username = forms.CharField(min_length=settings.USERNAME_MIN_LENGTH)
    password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password")

    def clean_username(self) -> str:
        username = self.cleaned_data["username"]
        if get_user_model().objects.filter(username__iexact=username):
            raise forms.ValidationError(ValidationErrors.USERNAME_TAKEN)
        return username

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
            query = {"email": username_or_email}
        else:
            query = {"username": username_or_email}

        user: Optional[User]

        try:
            user = get_user_model().objects.get(**query)
            if not user.is_active:
                raise forms.ValidationError(ValidationErrors.ACCOUNT_DEACTIVATED)
        except get_user_model().DoesNotExist:
            raise forms.ValidationError(ValidationErrors.AUTH_ERROR)

        user = cast(
            Optional[User], authenticate(username=user.username, password=password)
        )

        if not user:
            raise forms.ValidationError(ValidationErrors.AUTH_ERROR)

        if user.is_superuser:
            raise forms.ValidationError(ValidationErrors.SUPERUSER_LOGIN)

        self.cleaned_data["user"] = user
        return self.cleaned_data


class UpdateUserForm(SkoleModelForm):

    username = forms.CharField(min_length=settings.USERNAME_MIN_LENGTH)
    avatar = forms.CharField(required=False)

    avatar_operation: Optional[FieldOperation] = None

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "title", "bio", "avatar", "school", "subject")

    def clean_avatar(self) -> Union[File, str]:
        avatar, self.avatar_operation = clean_file_field(
            form=self, field_name="avatar", created_file_name="avatar"
        )
        return avatar

    def save(self, commit: bool = True) -> User:
        self.instance = super().save(commit)
        if self.avatar_operation == FieldOperation.NEW_VALUE:
            clean_metadata(self.instance.avatar.path)
        return self.instance


class ChangePasswordForm(SkoleModelForm):
    old_password = forms.CharField()
    new_password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)

    class Meta:
        model = get_user_model()
        fields = ("old_password", "new_password")

    def clean_old_password(self) -> None:
        old_password = self.cleaned_data["old_password"]

        if not self.instance.check_password(old_password):
            raise forms.ValidationError(ValidationErrors.INVALID_OLD_PASSWORD)

        return old_password


class SetPasswordForm(TokenForm):
    new_password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)


class DeleteUserForm(SkoleModelForm):
    class Meta:
        model = get_user_model()
        fields = ("password",)

    def clean_password(self) -> None:
        password = self.cleaned_data["password"]

        if not self.instance.check_password(password):
            raise forms.ValidationError(ValidationErrors.INVALID_PASSWORD)

        return password
