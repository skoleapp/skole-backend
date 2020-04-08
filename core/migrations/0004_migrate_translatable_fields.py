from django.db import migrations
from django.conf import settings

LANGUGE_CODES = [code for code, _ in settings.LANGUAGES]


# Ignore: One-off thing, no need to bother typing these.
def forwards_func(apps, schema_editor):  # type: ignore
    for model in ("City", "Country", "ResourceType", "School", "SchoolType", "Subject"):
        MyModel = apps.get_model("core", model)
        MyModelTranslation = apps.get_model("core", f"{model}Translation")

        for obj in MyModel.objects.all():
            for code in LANGUGE_CODES:
                MyModelTranslation.objects.create(
                    master_id=obj.pk, language_code=code, name_t=obj.name,
                )


def backwards_func(apps, schema_editor):  # type: ignore
    for model in ("City", "Country", "ResourceType", "School", "SchoolType", "Subject"):
        MyModel = apps.get_model("core", model)
        MyModelTranslation = apps.get_model("core", f"{model}Translation")

        for obj in MyModel.objects.all():
            for code in LANGUGE_CODES:
                translation = MyModelTranslation.objects.filter(master_id=obj.pk).get(
                    language_code=code
                )
                obj.name = translation.name_t
                obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_add_translation_model"),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
