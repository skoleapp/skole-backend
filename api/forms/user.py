from typing import cast

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _
from mypy.types import JsonDict

from api.utils.messages import AUTH_ERROR_MESSAGE
from core.models import BetaCode, User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)
    code = forms.CharField(max_length=8)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password", "code")

    def clean_code(self) -> BetaCode:
        code = self.cleaned_data["code"]
        try:
            beta_code = BetaCode.objects.filter(usages__gt=0).get(code=code)
        except BetaCode.DoesNotExist:
            raise forms.ValidationError(_("Invalid beta register code."))
        return beta_code


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
            user = authenticate(
                username=get_user_model().objects.get(**kwargs).email, password=password
            )
            user = cast(User, user)

            if not user:
                raise forms.ValidationError(AUTH_ERROR_MESSAGE, code="authentication")

            if user.is_superuser:
                raise forms.ValidationError(
                    _("Cannot log in as superuser."), code="authentication"
                )

            self.cleaned_data["user"] = user
            return self.cleaned_data

        except get_user_model().DoesNotExist:
            raise forms.ValidationError(AUTH_ERROR_MESSAGE, code="authentication")


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "title", "bio", "avatar")

    def clean_avatar(self) -> str:
        # Ignore: Mypy considers files as optional but they're always at least an empty MultiValueDict.
        if avatar := self.files.get("1", None):  # type: ignore [union-attr]
            return avatar
        else:
            return self.cleaned_data["avatar"]

    def clean_email(self) -> str:
        email = self.cleaned_data["email"]
        if (
            get_user_model()
            .objects.exclude(pk=self.instance.pk)
            .filter(email__iexact=email)
        ):
            raise forms.ValidationError(_("This email is taken."))
        return email

    def clean_username(self) -> str:
        username = self.cleaned_data["username"]
        if (
            get_user_model()
            .objects.exclude(pk=self.instance.pk)
            .filter(username__exact=username)
        ):
            raise forms.ValidationError(_("This username is taken."))
        return username


class ChangePasswordForm(forms.ModelForm):
    old_password = forms.CharField()
    new_password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)

    class Meta:
        model = get_user_model()
        fields = ("old_password", "new_password")

    def clean_old_password(self) -> None:
        old_password = self.cleaned_data["old_password"]
        if not self.instance.check_password(old_password):
            raise forms.ValidationError(_("Incorrect old password."))

        return old_password


class DeleteUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("password",)

    def clean_password(self) -> None:
        password = self.cleaned_data["password"]

        if not self.instance.check_password(password):
            raise forms.ValidationError(_("Incorrect password."))

        return password
