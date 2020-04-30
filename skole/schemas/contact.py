from smtplib import SMTPException

import graphene
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from graphene_django.forms.mutation import DjangoFormMutation
from graphql import ResolveInfo

from skole.forms.contact import ContactForm
from skole.utils.constants import Messages, MutationErrors
from skole.utils.mixins import MessageMixin


class ContactMutation(MessageMixin, DjangoFormMutation):
    class Meta:
        form_class = ContactForm

    @classmethod
    def perform_mutate(cls, form: ContactForm, info: ResolveInfo) -> "ContactMutation":
        subject = form.cleaned_data.get("subject")
        email = form.cleaned_data.get("email")
        message = form.cleaned_data.get("message")

        context = {
            "subject": subject,
            "message": message,
        }

        subject_template = settings.EMAIL_SUBJECT_CONTACT
        message_template = settings.EMAIL_TEMPLATE_CONTACT

        subject = render_to_string(subject_template, context).replace("\n", " ").strip()
        html_message = render_to_string(message_template, context)
        message = strip_tags(html_message)

        try:
            send_mail(
                subject=subject,
                from_email=email,
                message=message,
                html_message=html_message,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )

            return cls(message=Messages.MESSAGE_SENT)
        except SMTPException:
            return cls(errors=MutationErrors.EMAIL_ERROR)


class Mutation(graphene.ObjectType):
    create_contact_message = ContactMutation.Field()
