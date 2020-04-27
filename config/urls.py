from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from skole.views import CustomGraphQLView, health_check

urlpatterns = [
    # FIXME: make frontend work without exempt.
    path(
        "graphql/",
        csrf_exempt(CustomGraphQLView.as_view(graphiql=bool(settings.DEBUG))),
    ),
    path("healthz/", health_check),
]

urlpatterns += i18n_patterns(path("admin/", admin.site.urls))

if settings.DEBUG:
    # Static files are handled with the staticfiles app.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
