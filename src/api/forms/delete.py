from django import forms
from graphene_django.forms import GlobalIDFormField


class DeleteObjectForm(forms.Form):
    comment = GlobalIDFormField()
    resource = GlobalIDFormField()
    resource_part = GlobalIDFormField()
    vote = GlobalIDFormField()
