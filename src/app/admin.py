from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model

app = apps.get_app_config("app")

for model_name, model in app.models.items():
    if "user" not in model_name:
        admin.site.register(model)

admin.site.register(get_user_model())
