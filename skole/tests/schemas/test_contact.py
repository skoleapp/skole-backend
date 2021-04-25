from __future__ import annotations

from django.conf import settings
from django.core import mail

from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import JsonDict


class ContactSchemaTests(SkoleSchemaTestCase):
    def mutate_create_contact_message(
        self,
        *,
        subject: str,
        name: str,
        email: str,
        message: str,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="createContactMessage",
            input_type="ContactMutationInput!",
            input={
                "subject": subject,
                "name": name,
                "email": email,
                "message": message,
            },
            result="successMessage",
        )

    def test_create_contact_message(self) -> None:
        subject = "some subject"
        name = "John Smith"
        email = "somemail@test.test"
        message = "This is a message."
        res = self.mutate_create_contact_message(
            subject=subject, name=name, email=email, message=message
        )
        assert not res["errors"]

        assert len(mail.outbox) == 1
        sent = mail.outbox[0]

        assert sent.from_email == settings.EMAIL_CONTACT_FORM_SENDER
        assert sent.to == [settings.EMAIL_ADDRESS]

        assert subject in sent.subject
        assert name in sent.body
        assert email in sent.body
        assert message in sent.body
