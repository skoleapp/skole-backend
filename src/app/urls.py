from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

import settings

urlpatterns = [
    path(r"admin/", admin.site.urls),
    path(r"graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True))),
]

if settings.DEBUG:
    # Just for being explicit, these wouldn't and shouldn't work in production mode anyways.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
