from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from parler.models import TranslatedFieldsModelMixin

core = apps.get_app_config("core")

for model_name, model in core.models.items():
    if "user" not in model_name:
        admin.site.register(model)

admin.site.register(get_user_model())
admin.site.site_header = "Skole Administration"

# We monkey patch the method here so that it's used for every single translated model.
# Without this would just be displayed as "Finnish" or "English" in the object list.
TranslatedFieldsModelMixin.__str__ = (
    lambda self: f"{self.master} - {self.language_code}"
)
