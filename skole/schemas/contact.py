from smtplib import SMTPException

import graphene
from django.conf import settings
from django.core.mail import send_mail
from graphene_django.forms.mutation import DjangoFormMutation
from graphql import ResolveInfo

from skole.forms.contact import ContactForm
from skole.utils.constants import Messages, MutationErrors


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
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )

            return cls(message=Messages.MESSAGE_SENT)
        except SMTPException as e:
            # This error will show among the general errors in the frontend form.
            return cls(errors=MutationErrors.EMAIL_ERROR)


class Mutation(graphene.ObjectType):
    create_message = ContactMutation.Field()
