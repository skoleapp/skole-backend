from __future__ import annotations

from django.db import migrations

SEQUENCE_QUERY = """
SELECT setval('skole_thread_id_seq', COALESCE(MAX("id"), 1), MAX("id") IS NOT NULL) FROM "skole_thread";
DROP SEQUENCE "skole_course_id_seq";
ALTER SEQUENCE "skole_referralcode_id_seq" RENAME TO "skole_invitecode_id_seq";
"""


class Migration(migrations.Migration):
    """
    Make all sequences match their table names.

    This is meant to fix the problem which migrations 0031 and 0044 caused where we
    would get `duplicate key value violates unique constraint "skole_course_pkey"`
    errors when creating Threads. Somehow after 0044 we would have both
    `skole_course_id_seq` and `skole_thread_id_seq` and both of them would be attached
    to the `skole_threads` table. After loading the test data in, the former would be
    correctly at ID 27, but the latter would be at 1, and the app would use the latter.

    Surprisingly Django doesn't enforce keeping table and sequence names in sync
    automatically: https://code.djangoproject.com/ticket/23577. Nevertheless, we still
    shouldn't face this issue, and it's most likely a separate bug.
    """

    dependencies = [
        ("skole", "0053_install_trigram_extension"),
    ]

    operations = [
        migrations.RunSQL(SEQUENCE_QUERY),
    ]
