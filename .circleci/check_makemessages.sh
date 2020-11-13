#!/bin/sh

# CircleCI runs this script in the container to verify that makemessages
# was run and thus the translation files are all up-to-date.

for path in skole/locale/*; do
    lang=$(basename "$path")

    cp "skole/locale/$lang/LC_MESSAGES/django.po" "/tmp/$lang.po"
done

python manage.py makemessages --all 

for path in skole/locale/*; do
    lang=$(basename "$path")

    diff --unified=0 "skole/locale/$lang/LC_MESSAGES/django.po" "/tmp/$lang.po" \
        | grep -Ev -- '---|\+\+\+|^@@.*@@$|POT-Creation-Date' \
    && error=1 || echo "Makemessages ok for $lang."

    cp "/tmp/$lang.po" "skole/locale/$lang/LC_MESSAGES/django.po"
done

[ -z $error ] || { printf '\nForgotten to run makemessages.\nExiting with error!\n' && exit 1; }

echo 'All makemessages ok.'
