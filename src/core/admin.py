from django.contrib import admin
from django.contrib.auth import get_user_model

from core.models import School

admin.site.register(get_user_model())
admin.site.register(School)
