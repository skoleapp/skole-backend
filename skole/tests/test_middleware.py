import graphene_django.views
from django.conf import settings
from django.test import override_settings

from skole.models import DailyVisit
from skole.tests.helpers import SkoleSchemaTestCase, reload_module


class MiddlewareTests(SkoleSchemaTestCase):
    # language=GraphQL
    schema_query = """
        query Schema {
            __schema {
                types {
                    name
                    description
                }
            }
        }
    """
    # language=GraphQL
    user_query = """
        query User($slug: String) {
            user(slug: $slug) {
                slug
                username
            }
        }
    """

    def test_introspection_enabled(self) -> None:
        # Calling `override_settings` will trigger
        # `graphene_django.settings.reload_graphene_settings` just fine.
        # One could think that that's enough to get the new middleware config
        # into use, but because `graphene_django.views` has already imported
        # `graphene_settings`, and `reload_graphene_settings` simply reassigns the
        # name, the object in the `views` module will keep pointing to the original
        # settings instance. Thus we have to manually reload the whole module,
        # to make sure that the `graphene_settings` name in the `views` module
        # will point to the refreshed object. Only that way when our view class is
        # initialized its `middleware` attribute will correctly get the new value.
        #
        # The context manager also reloads the module again afterwards so that the
        # next tests will just use the middleware settings from `settings.py`.
        with reload_module(graphene_django.views) as loader:
            with override_settings(GRAPHENE=settings.GRAPHENE | {"MIDDLEWARE": []}):
                loader()
                res = self.execute(self.schema_query)
                assert isinstance(res["types"][0]["name"], str)

                slug = "testuser2"
                res = self.execute(self.user_query, variables={"slug": slug})
                assert res["slug"] == slug

    def test_introspection_disabled(self) -> None:
        with reload_module(graphene_django.views) as loader:
            with override_settings(
                GRAPHENE=settings.GRAPHENE
                | {"MIDDLEWARE": ["skole.middleware.DisableIntrospectionMiddleware"]}
            ):
                loader()
                self.execute(self.schema_query, assert_error=True)

                # Fine to make a query which doesn't introspect the schema.
                slug = "testuser2"
                res = self.execute(self.user_query, variables={"slug": slug})
                assert res["slug"] == slug

    def test_track_visits_middleware(self) -> None:
        self.authenticated_user = 2
        user = self.get_authenticated_user()
        assert DailyVisit.objects.filter(user__pk=user.pk).count() == 0

        self.execute(self.user_query, variables={"slug": user.slug})
        self.execute(self.user_query, variables={"slug": user.slug})
        self.execute(self.user_query, variables={"slug": user.slug})
        assert DailyVisit.objects.filter(user__pk=user.pk).count() == 1
        visit = DailyVisit.objects.get(user__pk=user.pk)
        assert visit.visits == 3
