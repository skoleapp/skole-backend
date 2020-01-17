from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from mypy.types import JsonDict

from api.utils.messages import (EMAIL_TAKEN_MESSAGE,
                                INCORRECT_OLD_PASSWORD_MESSAGE,
                                INCORRECT_PASSWORD_MESSAGE,
                                UNABLE_TO_AUTHENTICATE_MESSAGE,
                                USERNAME_TAKEN_MESSAGE, email_error_messages,
                                username_error_messages)


class SignUpForm(forms.ModelForm):
    username = forms.CharField(error_messages=username_error_messages)
    email = forms.EmailField(error_messages=email_error_messages)
    password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password")


class SignInForm(forms.ModelForm):
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
                raise forms.ValidationError(UNABLE_TO_AUTHENTICATE_MESSAGE, code="authentication")

            self.cleaned_data["user"] = user
            return self.cleaned_data

        except get_user_model().DoesNotExist:
            raise forms.ValidationError(UNABLE_TO_AUTHENTICATE_MESSAGE, code="authentication")


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(error_messages=username_error_messages)
    email = forms.EmailField(error_messages=email_error_messages)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "title", "bio", "avatar")

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
        old_password = self.cleaned_data["old_password"]
        if not self.instance.check_password(old_password):
            raise forms.ValidationError(INCORRECT_OLD_PASSWORD_MESSAGE)

        return old_password


class DeleteUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("password",)

    def clean_password(self) -> None:
        password = self.cleaned_data["password"]

        if not self.instance.check_password(password):
            raise forms.ValidationError(INCORRECT_PASSWORD_MESSAGE)

        return password
