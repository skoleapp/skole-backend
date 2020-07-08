from django import forms

from skole.models import Activity


class MarkActivityReadForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ("id", "read",)
