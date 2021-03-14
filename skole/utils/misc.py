import re

import autoslug.utils

NON_ALPHANUM = re.compile(r"[^a-zA-Z0-9]")


def slugify(value: str) -> str:
    """
    Improves upon `autoslug.utils.slugify` by preventing trailing special characters.

    In practice this happens so that this makes sure that the char at the 50th index
    is not a special character. If it is, this replaces it with the letter 'a'.

    Used as the `AUTOSLUG_SLUGIFY_FUNCTION` in `settings.py`.

    Examples:
        >>> slugify("b" * 49 + "-b")
        'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbab'
        >>> slugify(50 * "b")
        'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        >>> slugify("_____")
        '_____'
    """
    slug = autoslug.utils.slugify(value)
    try:
        if re.match(NON_ALPHANUM, slug[49]):
            slug = slug[:49] + "a" + slug[50:]
    except IndexError:
        pass
    return slug
