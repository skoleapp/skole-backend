from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from graphene_django.views import GraphQLView

urlpatterns = [
    path(r"admin/", admin.site.urls),
    path(r"graphql/", GraphQLView.as_view(graphiql=True))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
