import os
from smtplib import SMTPException

import graphene
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from graphene_django.forms.mutation import DjangoFormMutation
from graphql import ResolveInfo

from api.forms.contact import ContactForm


class ContactMutation(DjangoFormMutation):
    message = graphene.String()

    class Meta:
        form_class = ContactForm

    @classmethod
    def perform_mutate(cls, form: ContactForm, info: ResolveInfo) -> "ContactMutation":
        subject = form.cleaned_data.get("subject")
        name = form.cleaned_data.get("name")
        email = form.cleaned_data.get("email")
        message = form.cleaned_data.get("message")

        message = f"""\
            Message: {message}
            Name: {name}"""

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=email,
                recipient_list=[os.environ.get("EMAIL_URL", default="")],
                fail_silently=False,
            )

            return cls(message=_("Message sent successfully!"))
        except SMTPException as e:
            # This error will show among the general errors in the frontend form.
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        "messages": [_("Error while sending message.")],
                    }
                ]
            )


class Mutation(graphene.ObjectType):
    contact = ContactMutation.Field()
