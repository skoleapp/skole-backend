from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import ID, JsonDict


class SitemapTests(SkoleSchemaTestCase):
    authenticated_user: ID = None

    # language=GraphQL
    sitemap_fields = """
        fragment sitemapFields on SitemapObjectType {
            courses {
              id
              modified
            }
            resources {
              id
              modified
            }
            schools {
              id
              modified
            }
            users {
              id
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
        assert "courses" in sitemap
        assert "resources" in sitemap
        assert "schools" in sitemap
        assert "users" in sitemap
        assert sitemap["courses"][0]["id"] == "1"
        assert sitemap["courses"][0]["modified"] == "2020-01-01"
        assert sitemap["resources"][0]["id"] == "1"
        assert sitemap["resources"][0]["modified"] == "2020-01-01"
        assert sitemap["users"][0]["id"] == "1"
        assert sitemap["users"][0]["modified"] == "2020-01-01"
        assert sitemap["schools"][-1]["id"] == "6"
        assert sitemap["schools"][-1]["modified"] is None

        # Works when logged in (although this is really pointless)
        self.authenticated_user = 2
        sitemap = self.query_sitemap()
        assert len(sitemap) == 4
