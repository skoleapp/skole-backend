from skole.models import Badge
from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import JsonDict


class BadgeSchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    badge_fields = """
        fragment badgeFields on BadgeObjectType {
            id
            name
            description
            tier
        }
    """

    def query_badges(self) -> list[JsonDict]:
        # language=GraphQL
        graphql = (
            self.badge_fields
            + """
            query Badges {
                badges {
                    ...badgeFields
                }
            }
            """
        )

        return self.execute(graphql)

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.badge_fields)

    def test_badges(self) -> None:
        badges = self.query_badges()
        assert len(badges) == Badge.objects.count()
        assert badges[0]["id"] == "1"
        assert badges[0]["name"] == "Staff"
        assert badges[0]["description"] == "Skole staff."
        assert badges[0]["tier"] == "DIAMOND"
