from django import forms

from .base import SkoleForm


class ContactForm(SkoleForm):
    subject = forms.CharField(max_length=25, required=False)
    name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(required=False)
    message = forms.CharField(max_length=2000)
