from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from api.views import CustomGraphQLView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "graphql/",
        csrf_exempt(CustomGraphQLView.as_view(graphiql=bool(settings.DEBUG))),
    ),
]

if settings.DEBUG:
    # Static files are handled with the staticfiles app.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
