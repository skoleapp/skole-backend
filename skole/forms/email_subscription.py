from django import forms
from django.contrib.auth import get_user_model

from skole.forms.base import SkoleModelForm
from skole.models import EmailSubscription
from skole.utils.constants import ValidationErrors


class CreateEmailSubscriptionForm(SkoleModelForm):
    class Meta:
        model = EmailSubscription
        fields = ("email",)

    def clean_email(self) -> str:
        # Call `lower()` since we want all saved email to be lowercase.
        email = self.cleaned_data["email"].lower()

        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(ValidationErrors.ACCOUNT_EMAIL)

        return email


class UpdateEmailSubscriptionForm(SkoleModelForm):
    token = forms.CharField(required=False)

    class Meta:
        model = EmailSubscription
        fields = (
            "product_updates",
            "blog_posts",
        )

    def save(self, commit: bool = True) -> EmailSubscription:
        # Prevent saving instance here - a custom handler is implemented in the schema.
        return self.instance
