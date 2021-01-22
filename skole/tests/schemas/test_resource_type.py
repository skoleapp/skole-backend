from typing import cast

from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import JsonDict


class ResourceTypeSchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    resource_type_fields = """
        fragment resourceTypeFields on ResourceTypeObjectType {
            id
            name
        }
    """

    def query_autocomplete_resource_types(self) -> list[JsonDict]:
        # language=GraphQL
        graphql = (
            self.resource_type_fields
            + """
            query AutocompleteResourceTypes {
                autocompleteResourceTypes {
                    ...resourceTypeFields
                }
            }
            """
        )

        return cast(list[JsonDict], self.execute(graphql))

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.resource_type_fields)

    def test_autocomplete_resource_types(self) -> None:
        resource_types = self.query_autocomplete_resource_types()
        assert len(resource_types) == 4
        # ResourceTypes should be ordered by IDs.
        assert resource_types[0]["id"] == "1"
        assert resource_types[0]["name"] == "Exercise"
        assert resource_types[1]["id"] == "2"
        assert resource_types[1]["name"] == "Note"
