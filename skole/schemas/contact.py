from __future__ import annotations

from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from graphene_django.forms.mutation import DjangoFormMutation

from skole.forms import ContactForm
from skole.schemas.base import SkoleCreateUpdateMutationMixin, SkoleObjectType
from skole.schemas.mixins import SuccessMessageMixin
from skole.types import ResolveInfo
from skole.utils.constants import Messages, MutationErrors


class ContactMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoFormMutation
):
    """Submit a message via the contact form."""

    class Meta:
        form_class = ContactForm

    @classmethod
    def perform_mutate(cls, form: ContactForm, info: ResolveInfo) -> ContactMutation:
        subject = form.cleaned_data.get("subject")
        name = form.cleaned_data.get("name")
        email = form.cleaned_data.get("email")
        message = form.cleaned_data.get("message")

        context = {
            "subject": subject,
            "message": message,
            "name": name if name != "" else "-",
            "email": email,
        }

        html_message = render_to_string("email/contact.html", context)
        message = strip_tags(html_message)

        try:
            send_mail(
                subject=subject,
                from_email=settings.EMAIL_CONTACT_FORM_SENDER,
                message=message,
                html_message=html_message,
                recipient_list=[settings.EMAIL_ADDRESS],
                fail_silently=False,
            )

            return cls(success_message=Messages.MESSAGE_SENT)
        except SMTPException:
            return cls(errors=MutationErrors.EMAIL_ERROR)


class Mutation(SkoleObjectType):
    create_contact_message = ContactMutation.Field()
