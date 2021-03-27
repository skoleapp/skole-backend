from django.contrib.auth import get_user_model

from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import ID, JsonDict


class SitemapTests(SkoleSchemaTestCase):
    authenticated_user: ID = None

    # language=GraphQL
    sitemap_fields = """
        fragment sitemapFields on SitemapObjectType {
            threads {
              slug
              modified
            }
            resources {
              slug
              modified
            }
            schools {
              slug
              modified
            }
            users {
              slug
              modified
            }
        }
    """

    def query_sitemap(self) -> JsonDict:
        # language=GraphQL
        graphql = (
            self.sitemap_fields
            + """
            query Sitemap {
                sitemap {
                    ...sitemapFields
                }
            }
            """
        )
        return self.execute(graphql)

    def test_field_fragment(self) -> None:
        self.assert_field_fragment_matches_schema(self.sitemap_fields)

    def test_sitemap(self) -> None:
        # Works when not logged in
        sitemap = self.query_sitemap()
        assert len(sitemap) == 4
        assert "threads" in sitemap
        assert "resources" in sitemap
        assert "schools" in sitemap
        assert "users" in sitemap
        assert sitemap["threads"][0]["slug"] == "test-thread-1"
        assert sitemap["threads"][0]["modified"] == "2020-01-01"
        assert sitemap["resources"][0]["slug"] == "sample-exam-1-2012-12-12"
        assert sitemap["resources"][0]["modified"] == "2020-01-01"
        assert sitemap["users"][0]["slug"] == "testuser2"
        assert sitemap["users"][0]["modified"] == "2020-01-01"
        assert sitemap["schools"][0]["slug"] == "university-of-turku"
        assert not sitemap["schools"][0]["modified"]

        # Test that no superusers are included in sitemap users.
        for user in sitemap["users"]:
            user_from_db = get_user_model().objects.get(slug=user["slug"])
            assert not user_from_db.is_superuser

        # Works when logged in (although this is really pointless)
        self.authenticated_user = 2
        sitemap = self.query_sitemap()
        assert len(sitemap) == 4
