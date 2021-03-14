import re

import autoslug.utils

TRAILING_NON_ALPHANUM = re.compile(r"[^a-zA-Z0-9]+$")


def slugify(value: str) -> str:
    """
    Improves upon `autoslug.utils.slugify` by preventing trailing special characters.

    This also pre-truncates the slug to 50 characters, which is the default for the
    `AutoSlugField.max_length`, and the value that we're always using. This would be
    done in the AutoSlugField after slugifying, but we need to do it here to make
    sure that the final character is alphanumeric.

    Used as the `AUTOSLUG_SLUGIFY_FUNCTION` in `settings.py`.

    Examples:
        >>> slugify("b" * 49 + "-aaa")
        'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        >>> slugify("b" * 49 + "--")
        'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        >>> slugify(50 * "b")
        'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        >>> slugify("_____")
        ''
    """
    slug = autoslug.utils.slugify(value)[:50]
    return re.sub(TRAILING_NON_ALPHANUM, "", slug)
