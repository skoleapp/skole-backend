# Generated by Django 3.1.7 on 2021-03-26 13:56
# Manually edited to add the `forwards_func`.
from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def forwards_func(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    """
    Transmogrify all Resources into Comments.

    Also move all comments of that
    """
    Resource = apps.get_model("skole", "Resource")
    Comment = apps.get_model("skole", "Comment")

    # We have very little Resources in the prod db, so these nested loops are just fine.

    for resource in Resource.objects.all():
        created_comment = Comment.objects.create(
            text=resource.title,
            file=resource.file,
            thread=resource.thread,
            user=resource.user,
        )

        Comment.objects.filter(pk__in=resource.comments.values("reply_comments")).update(comment=created_comment)
        resource.comments.update(resource=None, comment=created_comment)
        # No need to delete the resources now, we'll drop the whole model in the next
        # migration.


class Migration(migrations.Migration):

    dependencies = [
        ("skole", "0033_comment_file_image"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_func, reverse_code=migrations.RunPython.noop
        ),
    ]