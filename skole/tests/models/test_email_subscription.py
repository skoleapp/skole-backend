from django.core import signing

from skole.models import EmailSubscription
from skole.types import Fixture
from skole.utils.constants import TokenAction


def test_str(db: Fixture) -> None:
    email_subscription = EmailSubscription.objects.get(pk=1)
    assert str(email_subscription) == "subscriber@test.com"


def test_update_email_subscription(db: Fixture) -> None:
    email = "test2@test.com"
    email_subscription = EmailSubscription.objects.create(email=email)
    assert email_subscription.email == email
    assert email_subscription.product_updates
    assert email_subscription.blog_posts

    # Unsubscribe from product updates.

    payload = {"email": email, "action": TokenAction.UPDATE_EMAIL_SUBSCRIPTION}
    token = signing.dumps(payload)

    obj, deleted = EmailSubscription.objects.update_email_subscription(
        token=token,
        product_updates=False,
        blog_posts=True,
    )

    assert obj is not None
    assert not deleted
    assert not obj.product_updates
    assert obj.blog_posts

    # Unsubscribe from blog posts.

    obj, deleted = EmailSubscription.objects.update_email_subscription(
        token=token,
        product_updates=True,
        blog_posts=False,
    )

    assert obj is not None
    assert not deleted
    assert obj.product_updates
    assert not obj.blog_posts

    # Unsubscribe from all marketing email.

    _, deleted = EmailSubscription.objects.update_email_subscription(
        token=token,
        product_updates=False,
        blog_posts=False,
    )

    assert deleted
