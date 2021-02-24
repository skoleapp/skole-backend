from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from skole.models import EmailSubscription, MarketingEmail


class AdminTests(TestCase):
    fixtures = ["test-data.yaml"]

    def test_send_marketing_email(self) -> None:
        url = reverse("admin:skole_marketingemail_changelist")
        self.client.login(username="admin", password="admin")

        # Test sending product update email.

        product_update_subscriber_count = 10

        data = {
            "action": "send_marketing_email",
            "_selected_action": [1],
            "_confirm_action": True,
        }

        res = self.client.post(url, data=data, follow=True)
        assert res.status_code == 200
        assert "Successfully sent email" in str(list(get_messages(res.wsgi_request))[0])
        assert len(mail.outbox) == product_update_subscriber_count
        marketing_email = MarketingEmail.objects.get(pk=1)

        # Test that only people who have subscribed to product updates are in the recipient list.
        for sent in mail.outbox:
            assert sent.from_email == str(marketing_email.from_email)
            assert sent.subject == marketing_email.subject

            recipient = sent.to[0]
            user = get_user_model().objects.get_or_none(email=recipient)

            if user:
                assert user.product_update_email_permission
            else:
                email_subscription = EmailSubscription.objects.get(email=recipient)
                assert email_subscription.product_updates

        # Test sending blog post email.

        blog_post_subscriber_count = 8

        data = {
            "action": "send_marketing_email",
            "_selected_action": [2],
            "_confirm_action": True,
        }

        res = self.client.post(url, data=data, follow=True)
        assert res.status_code == 200
        assert "Successfully sent email" in str(list(get_messages(res.wsgi_request))[0])
        assert (
            len(mail.outbox)
            == product_update_subscriber_count + blog_post_subscriber_count
        )
        marketing_email = MarketingEmail.objects.get(pk=2)

        # Test that only people who have subscribed to blog posts are in the recipient list.
        for sent in mail.outbox[product_update_subscriber_count:]:
            assert sent.from_email == str(marketing_email.from_email)
            assert sent.subject == marketing_email.subject

            recipient = sent.to[0]
            user = get_user_model().objects.get_or_none(email=recipient)

            if user:
                assert user.blog_post_email_permission
            else:
                email_subscription = EmailSubscription.objects.get(email=recipient)
                assert email_subscription.blog_posts

        # Test sending same email again.
        res = self.client.post(url, data=data, follow=True)
        assert res.status_code == 200
        assert "The following email has already been sent" in str(
            list(get_messages(res.wsgi_request))[0]
        )
        assert (
            len(mail.outbox)
            == product_update_subscriber_count + blog_post_subscriber_count
        )

        self.client.logout()
