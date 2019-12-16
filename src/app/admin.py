from django.contrib import admin
from django.contrib.auth import get_user_model

from app.models import City
from app.models import Country
from app.models import Course
from app.models import Resource
from app.models import ResourceType
from app.models import School
from app.models import SchoolType

admin.site.register(City)
admin.site.register(Country)
admin.site.register(Course)
admin.site.register(Resource)
admin.site.register(ResourceType)
admin.site.register(School)
admin.site.register(SchoolType)
admin.site.register(get_user_model())
