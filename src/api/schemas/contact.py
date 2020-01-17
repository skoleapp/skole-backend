import os
from smtplib import SMTPException

import graphene
from api.forms.contact import ContactForm
from api.utils.messages import MESSAGE_SENT_ERROR_MESSAGE, MESSAGE_SENT_SUCCESS_MESSAGE
from django.core.mail import send_mail
from graphene_django.forms.mutation import DjangoFormMutation
from graphql import ResolveInfo


class ContactMutation(DjangoFormMutation):
    message = graphene.String()

    class Meta:
        form_class = ContactForm

    @classmethod
    def perform_mutate(cls, form: ContactForm, info: ResolveInfo) -> "ContactMutation":
        """
        TODO: Set up email settings: https://docs.djangoproject.com/en/2.2/topics/email/.
        """

        try:
            send_mail(
                subject=form.cleaned_data["contact_type"],
                message=form.cleaned_data["message"],
                from_email=form.cleaned_data["email"],
                recipient_list=[os.environ.get("SKOLE_INFO_EMAIL")],
                fail_silently=False,
            )

            return cls(message=MESSAGE_SENT_SUCCESS_MESSAGE)
        except SMTPException as e:
            # This error will show among the general errors in the frontend form.
            return cls(
                errors=[{"field": "__all__", "messages": [MESSAGE_SENT_ERROR_MESSAGE]}]
            )


class Mutation(graphene.ObjectType):
    contact = ContactMutation.Field()
