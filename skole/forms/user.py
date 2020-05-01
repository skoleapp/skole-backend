from typing import cast

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from mypy.types import JsonDict

from skole.models import BetaCode, User
from skole.utils.constants import ValidationErrors


class RegisterForm(forms.ModelForm):
    username = forms.CharField(min_length=settings.USERNAME_MIN_LENGTH)
    password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)
    code = forms.CharField(max_length=8)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password", "code")

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
            kwargs = {"email": username_or_email}
        else:
            kwargs = {"username": username_or_email}

        try:
            existing_user = get_user_model().objects.get(**kwargs)
            if not existing_user.is_active:
                raise forms.ValidationError(ValidationErrors.ACCOUNT_DEACTIVATED)
        except User.DoesNotExist:
            pass

        try:
            user = authenticate(
                username=get_user_model().objects.get(**kwargs).username,
                password=password,
            )

            user = cast(User, user)

            if not user:
                raise forms.ValidationError(ValidationErrors.AUTH_ERROR)

            if user.is_superuser:
                raise forms.ValidationError(ValidationErrors.SUPERUSER_LOGIN)

            self.cleaned_data["user"] = user
            return self.cleaned_data

        except get_user_model().DoesNotExist:
            raise forms.ValidationError(ValidationErrors.AUTH_ERROR)


class UpdateUserForm(forms.ModelForm):

    username = forms.CharField(min_length=settings.USERNAME_MIN_LENGTH)
    avatar = forms.CharField(required=False)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "title", "bio", "avatar", "school", "subject")

    def clean_avatar(self) -> str:
        # Ignore: Mypy considers files as optional but they're always at least an empty MultiValueDict.
        if avatar := self.files.get("1", None):  # type: ignore [union-attr]
            return avatar  # New avatar.
        elif self.cleaned_data["avatar"] == "":
            return ""  # Avatar deleted.
        else:
            return self.instance.avatar  # Avatar not modified.

    def clean_username(self) -> str:
        username = self.cleaned_data["username"]
        if (
            get_user_model()
            .objects.exclude(pk=self.instance.pk)
            .filter(username__iexact=username)
        ):
            raise forms.ValidationError(ValidationErrors.USERNAME_TAKEN)
        return username

    def clean_email(self) -> str:
        email = self.cleaned_data["email"]
        if email != "" and (
            get_user_model()
            .objects.exclude(pk=self.instance.pk)
            .filter(email__iexact=email)
        ):
            raise forms.ValidationError(ValidationErrors.EMAIL_TAKEN)
        return email


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
