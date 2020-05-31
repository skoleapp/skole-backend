from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from skole.views import SkoleGraphQLView, health_check

urlpatterns = [
    path(
        "graphql/",
        csrf_exempt(SkoleGraphQLView.as_view(graphiql=bool(settings.DEBUG))),
    ),
    path("healthz/", health_check),
]

urlpatterns += i18n_patterns(path("admin/", admin.site.urls))

# Pragma: Lazy settings access makes it so this never true when running coverage.
if settings.DEBUG:  # pragma: no cover
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
