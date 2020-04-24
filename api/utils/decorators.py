from functools import wraps

from django.utils.translation import gettext_lazy as _


def login_required(fn):
    @wraps(fn)
    def wrapper(cls, root, info, **kwargs):
        user = info.context.user

        if not user.is_authenticated:
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        # TODO: Translate this.
                        "messages": [
                            _("This action is only allowed for authenticated users.")
                        ],
                    }
                ]
            )

        return fn(cls, root, info, **kwargs)

    return wrapper


def verification_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(cls, root, info, **kwargs):
        user = info.context.user
        if not user.status.verified:
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        # TODO: Translate this.
                        "messages": [
                            _(
                                "This action is only allowed for users who have verified their accounts. Please verify your account."
                            )
                        ],
                    }
                ]
            )

        return fn(cls, root, info, **kwargs)

    return wrapper
