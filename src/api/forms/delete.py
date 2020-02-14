from django import forms
from graphene_django.forms import GlobalIDFormField


class DeleteObjectForm(forms.Form):
    comment = GlobalIDFormField(required=False)
    resource = GlobalIDFormField(required=False)
    resource_part = GlobalIDFormField(required=False)
    vote = GlobalIDFormField(required=False)
