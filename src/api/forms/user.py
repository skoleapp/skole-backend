from django import forms
from django.conf import settings
from core.utils import JsonDict
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from ..utils import EMAIL_TAKEN_MESSAGE, USERNAME_TAKEN_MESSAGE, INCORRECT_OLD_PASSWORD

class RegisterForm(forms.ModelForm):
    password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password")


class LoginForm(forms.Form):
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
            user = get_user_model().objects.get(**kwargs)
            user = authenticate(username=user.email, password=password)

            if not user:
                msg = "Unable to authenticate with the provided credentials."
                raise forms.ValidationError(msg, code="authentication")

            self.cleaned_data["user"] = user

        except get_user_model().DoesNotExist:
            msg = "User with the given username or email does not exist!"
            raise forms.ValidationError(msg, code="authentication")


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "title", "bio", "avatar", "language")

    def clean_email(self) -> str:
        email = self.cleaned_data["email"]
        if get_user_model().objects.exclude(pk=self.instance.pk).filter(email__iexact=email):
            raise forms.ValidationError(EMAIL_TAKEN_MESSAGE)
        return email

    def clean_username(self) -> str:
        username = self.cleaned_data["username"]
        if get_user_model().objects.exclude(pk=self.instance.pk).filter(username__exact=username):
            raise forms.ValidationError(USERNAME_TAKEN_MESSAGE)
        return username


class ChangePasswordForm(forms.ModelForm):
    old_password = forms.CharField()
    new_password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)

    class Meta:
        model = get_user_model()
        fields = ("old_password", "new_password")

    def clean_old_password(self) -> None:
        if not self.instance.check_password(self.cleaned_data["old_password"]):
            raise forms.ValidationError(INCORRECT_OLD_PASSWORD)
