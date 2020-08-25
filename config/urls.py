from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from graphql_jwt.decorators import jwt_cookie

from skole.views import SkoleGraphQLView, health_check

urlpatterns = [
    path("graphql/", jwt_cookie(SkoleGraphQLView.as_view(graphiql=settings.DEBUG))),
    path("healthz/", health_check),
    path("", RedirectView.as_view(url=reverse_lazy("admin:index"))),
]

urlpatterns += i18n_patterns(path("admin/", admin.site.urls))

# Pragma: Lazy settings access makes it so this never true when running coverage.
if settings.DEBUG:  # pragma: no cover
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
