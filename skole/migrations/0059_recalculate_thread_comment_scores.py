from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.models import OuterRef, Subquery, Sum, Value
from django.db.models.functions import Coalesce


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:

    Thread = apps.get_model("skole", "Thread")
    Comment = apps.get_model("skole", "Comment")

    Thread.objects.update(
        score=Subquery(
            Thread.objects.filter(pk=OuterRef("pk"))
            .annotate(new_score=Coalesce(Sum("votes__status"), Value(0)))
            .values("new_score")[:1]
        )
    )
    Comment.objects.update(
        score=Subquery(
            Comment.objects.filter(pk=OuterRef("pk"))
            .annotate(new_score=Coalesce(Sum("votes__status"), Value(0)))
            .values("new_score")[:1]
        )
    )


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0058_add_score_comment_thread"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]
