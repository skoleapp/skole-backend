from django import forms


class ContactForm(forms.Form):
    contact_type = forms.CharField(max_length=25)
    email = forms.EmailField()
    message = forms.CharField(max_length=2000)
    
