from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from mypy.types import JsonDict
from app.models import Resource


class UploadResourceForm(forms.ModelForm):
    files = forms.FileField(widget=forms.FileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Resource
        fields = ("title", "resource_type", "course")
