from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model

core = apps.get_app_config("core")

for model_name, model in core.models.items():
    if "user" not in model_name:
        admin.site.register(model)

admin.site.register(get_user_model())
