from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from graphql_jwt.decorators import jwt_cookie

from skole.views import SkoleGraphQLView, health_check, sitemap

urlpatterns = [
    path(
        "graphql/",
        # We can use `csrf_exempt` here, because:
        # 1. Our JWT token cookie uses `SameSite=Lax` which prevents CSRF via POST.
        # 2. GraphQL doesn't allow mutations via GET requests.
        # 3. CORS blocks the client from reading any sensitive GET request responses.
        csrf_exempt(jwt_cookie(SkoleGraphQLView.as_view(graphiql=settings.DEBUG))),
    ),
    path("healthz/", health_check),
    path("sitemap/", sitemap),
    path("", RedirectView.as_view(url=reverse_lazy("admin:index"))),
    *i18n_patterns(path("admin/", admin.site.urls)),
    *static(prefix=settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
