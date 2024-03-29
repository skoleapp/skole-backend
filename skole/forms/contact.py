from __future__ import annotations

from django import forms

from skole.forms.base import SkoleForm


class ContactForm(SkoleForm):
    subject = forms.CharField(max_length=50, required=False)
    name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(required=False)
    message = forms.CharField(max_length=2000)
