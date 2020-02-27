from django import forms


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=25)
    name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField()
    message = forms.CharField(max_length=2000)
