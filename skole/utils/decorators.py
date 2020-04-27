from functools import wraps

from skole.utils.constants import MutationErrors

# TODO: Add types for these.


def login_required_mutation(fn):  # type: ignore [no-untyped-def]
    """Custom decorator for mutation that require authentication."""

    @wraps(fn)
    def wrapper(cls, root, info, **kwargs):  # type: ignore [no-untyped-def]
        user = info.context.user

        if not user.is_authenticated:
            return cls(errors=MutationErrors.AUTH_REQUIRED)

        return fn(cls, root, info, **kwargs)

    return wrapper


def verification_required_mutation(fn):  # type: ignore [no-untyped-def]
    """Custom decorator for mutations that require verification and authentication."""

    @wraps(fn)
    @login_required_mutation
    def wrapper(cls, root, info, **kwargs):  # type: ignore [no-untyped-def]
        user = info.context.user
        if not user.verified:
            return cls(errors=MutationErrors.VERIFICATION_REQUIRED)

        return fn(cls, root, info, **kwargs)

    return wrapper
