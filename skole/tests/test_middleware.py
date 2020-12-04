import importlib

import graphene_django.views
from django.conf import settings
from django.test import override_settings

from skole.tests.helpers import SkoleSchemaTestCase


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
    normal_query = """
        query Country($id: ID) {
            country(id: $id) {
                id
                name
            }
        }
    """

    def test_introspection_enabled(self) -> None:
        # Ignore: Mypy 0.790 doesn't yet understand Python 3.9's dict merging.
        with override_settings(GRAPHENE=settings.GRAPHENE | {"MIDDLEWARE": []}):  # type: ignore[operator]

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
            importlib.reload(graphene_django.views)

            res = self.execute(self.schema_query)
            assert isinstance(res["types"][0]["name"], str)

            res = self.execute(self.normal_query, variables={"id": 1})
            assert res["id"] == "1"

        # So that next tests will just use the middleware settings from `settings.py`.
        importlib.reload(graphene_django.views)

    def test_introspection_disabled(self) -> None:
        with override_settings(
            # Ignore: Mypy 0.790 doesn't yet understand Python 3.9's dict merging.
            GRAPHENE=settings.GRAPHENE  # type: ignore[operator]
            | {"MIDDLEWARE": ["skole.middleware.DisableIntrospectionMiddleware"]}
        ):
            importlib.reload(graphene_django.views)

            self.execute(self.schema_query, assert_error=True)

            res = self.execute(self.normal_query, variables={"id": 1})  # No error here.
            assert res["id"] == "1"

        importlib.reload(graphene_django.views)
