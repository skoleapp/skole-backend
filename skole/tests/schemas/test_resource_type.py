from typing import List, cast

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

    def query_auto_complete_resource_types(self) -> List[JsonDict]:
        # language=GraphQL
        graphql = (
            self.resource_type_fields
            + """
            query AutoCompleteResourceTypes {
                autoCompleteResourceTypes {
                    ...resourceTypeFields
                }
            }
            """
        )
        return cast(List[JsonDict], self.execute(graphql))

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.resource_type_fields)

    def test_auto_complete_resource_types(self) -> None:
        resource_types = self.query_auto_complete_resource_types()
        assert len(resource_types) == 4
        # ResourceTypes should be ordered by IDs.
        assert resource_types[0]["id"] == "1"
        assert resource_types[0]["name"] == "Exam"
        assert resource_types[1]["id"] == "2"
        assert resource_types[1]["name"] == "Exercise"
