import os
from smtplib import SMTPException

import graphene
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from graphene_django.forms.mutation import DjangoFormMutation
from graphql import ResolveInfo

from api.forms.contact import ContactForm
from core.models import Contact


class ContactMutation(DjangoFormMutation):
    message = graphene.String()

    class Meta:
        form_class = ContactForm

    @classmethod
    def perform_mutate(cls, form: ContactForm, info: ResolveInfo) -> "ContactMutation":
        contact_type = form.cleaned_data["contact_type"]
        message = form.cleaned_data["message"]
        user = info.context.user

        if not user.is_anonymous:
            user_or_email = user
        else:
            email = form.cleaned_data["email"]
            user_or_email = email

        Contact.objects.create_contact(
            contact_type=contact_type, message=message, user_or_email=user_or_email,
        )

        try:
            send_mail(
                subject=contact_type,
                message=message,
                from_email=email,
                recipient_list=[os.environ["SKOLE_INFO_EMAIL"]],
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
