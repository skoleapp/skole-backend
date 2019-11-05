from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model

from ..utils import EMAIL_TAKEN_MESSAGE, USERNAME_TAKEN_MESSAGE, INCORRECT_OLD_PASSWORD


class RegisterForm(forms.ModelForm):
    password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password")


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
