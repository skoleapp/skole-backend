from django.db import migrations
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def forwards_func(apps, schema_editor):
    for model in ('City', 'Country', 'ResourceType', 'School', 'SchoolType', 'Subject'):
        MyModel = apps.get_model('core', model)
        MyModelTranslation = apps.get_model('core', f'{model}Translation')

        for object in MyModel.objects.all():
            MyModelTranslation.objects.create(
                master_id=object.pk,
                language_code=settings.LANGUAGE_CODE,
            )

def backwards_func(apps, schema_editor):
    for model in ('City', 'Country', 'ResourceType', 'School', 'SchoolType', 'Subject'):
        MyModel = apps.get_model('core', model)
        MyModelTranslation = apps.get_model('core', f'{model}Translation')

        for object in MyModel.objects.all():
            translation = _get_translation(object, MyModelTranslation)
            object.save()   # Note this only calls Model.save()

def _get_translation(object, MyModelTranslation):
    translations = MyModelTranslation.objects.filter(master_id=object.pk)
    try:
        # Try default translation
        return translations.get(language_code=settings.LANGUAGE_CODE)
    except ObjectDoesNotExist:
        try:
            # Try default language
            return translations.get(language_code=settings.PARLER_DEFAULT_LANGUAGE_CODE)
        except ObjectDoesNotExist:
            # Maybe the object was translated only in a specific language?
            # Hope there is a single translation
            return translations.get()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_translation_model'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
