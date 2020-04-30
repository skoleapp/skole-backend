from django import forms


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=25)
    email = forms.EmailField()
    message = forms.CharField(max_length=2000)
