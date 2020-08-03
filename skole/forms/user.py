from typing import Union, cast

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.files.uploadedfile import UploadedFile
from mypy.types import JsonDict

from skole.models import BetaCode, User
from skole.utils.constants import ValidationErrors
from skole.utils.shortcuts import clean_file_field


class RegisterForm(forms.ModelForm):
    username = forms.CharField(min_length=settings.USERNAME_MIN_LENGTH)
    password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)
    code = forms.CharField(max_length=8)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "school", "subject", "password", "code")

    def clean_username(self) -> str:
        username = self.cleaned_data["username"]

        if get_user_model().objects.filter(username__iexact=username):
            raise forms.ValidationError(ValidationErrors.USERNAME_TAKEN)
        return username

    def clean_code(self) -> BetaCode:
        code = self.cleaned_data["code"]

        try:
            return BetaCode.objects.get(code=code)
        except BetaCode.DoesNotExist:
            raise forms.ValidationError(ValidationErrors.INVALID_BETA_CODE)


class TokenForm(forms.Form):
    # We don't make the token required because we don't want
    # to return error messages for that specific field but rather
    # general error messages as the token is always a hidden field.
    token = forms.CharField(required=False)


class EmailForm(forms.Form):
    email = forms.EmailField()


class LoginForm(forms.ModelForm):
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

        try:
            user = get_user_model().objects.get(**query)
            if not user.is_active:
                raise forms.ValidationError(ValidationErrors.ACCOUNT_DEACTIVATED)
        except get_user_model().DoesNotExist:
            raise forms.ValidationError(ValidationErrors.AUTH_ERROR)

        user = authenticate(username=user.username, password=password)

        if not user:
            raise forms.ValidationError(ValidationErrors.AUTH_ERROR)

        user = cast(User, user)

        if user.is_superuser:
            raise forms.ValidationError(ValidationErrors.SUPERUSER_LOGIN)

        self.cleaned_data["user"] = user
        return self.cleaned_data


class UpdateUserForm(forms.ModelForm):

    username = forms.CharField(min_length=settings.USERNAME_MIN_LENGTH)
    avatar = forms.CharField(required=False)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "title", "bio", "avatar", "school", "subject")

    def clean_avatar(self) -> Union[UploadedFile, str]:
        return clean_file_field(self, "avatar")


class ChangePasswordForm(forms.ModelForm):
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


class DeleteUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("password",)

    def clean_password(self) -> None:
        password = self.cleaned_data["password"]

        if not self.instance.check_password(password):
            raise forms.ValidationError(ValidationErrors.INVALID_PASSWORD)

        return password
