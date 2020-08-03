from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from graphql_jwt.decorators import jwt_cookie

from skole.views import SkoleGraphQLView, health_check

urlpatterns = [
    path(
        "graphql/",
        # FIXME: must remove the exempt now that the JWT token comes from cookies:
        #  https://django-graphql-jwt.domake.io/en/latest/authentication.html#per-cookie
        csrf_exempt(
            jwt_cookie(SkoleGraphQLView.as_view(graphiql=bool(settings.DEBUG)))
        ),
    ),
    path("healthz/", health_check),
    path("", RedirectView.as_view(url=reverse_lazy("admin:index"))),
]

urlpatterns += i18n_patterns(path("admin/", admin.site.urls))

# Pragma: Lazy settings access makes it so this never true when running coverage.
if settings.DEBUG:  # pragma: no cover
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
