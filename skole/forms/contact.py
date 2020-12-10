from django import forms

from .base import SkoleForm


class ContactForm(SkoleForm):
    subject = forms.CharField(max_length=25)
    name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField()
    message = forms.CharField(max_length=2000)
