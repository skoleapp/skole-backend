#!/bin/sh

# shellcheck disable=SC2016  # Backticks are fine in single quotes.

# CI pipeline runs this script in the container to verify that makemessages
# was run and thus the translation files are all up-to-date.

for path in skole/locale/*; do
    lang=$(basename "$path")

    cp "skole/locale/$lang/LC_MESSAGES/django.po" "/tmp/$lang.po"
done

python manage.py makemessages --all

for path in skole/locale/*; do
    lang=$(basename "$path")
    po_file="skole/locale/$lang/LC_MESSAGES/django.po"
    temp_file="/tmp/$lang.po"

    diff --unified=0 "$po_file" "$temp_file" | \
            grep --quiet --extended-regexp --invert-match -- '---|\+\+\+|^@@.*@@$|POT-Creation-Date' \
        && error=1 && printf 'Error! Makemessages not up-to-date for %s.\n' "$lang" \
        || printf 'Makemessages up-to-date for %s.\n' "$lang" \

    tail -n +2 "$po_file" | grep --quiet '^#, fuzzy$' \
        && error=1 && printf 'Error! `fuzzy` entries found in %s.\n' "$lang" \
        || printf 'No `fuzzy` message entries in %s.\n' "$lang"

    cp "$temp_file" "$po_file"
done

[ -z $error ] || { printf '\nExiting with error!\n' && exit 1; }

printf '\nAll makemessages ok.\n'
