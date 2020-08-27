from typing import List, cast

from mypy.types import JsonDict

from skole.tests.helpers import SkoleSchemaTestCase


class ResourceTypeSchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    resource_type_fields = """
        fragment resourceTypeFields on ResourceTypeObjectType {
            id
            name
        }
    """

    def query_resource_types(self) -> List[JsonDict]:
        # language=GraphQL
        graphql = (
            self.resource_type_fields
            + """
            query ResourceTypes {
                resourceTypes {
                    ...resourceTypeFields
                }
            }
            """
        )
        return cast(List[JsonDict], self.execute(graphql))

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.resource_type_fields)

    def test_resource_types(self) -> None:
        resource_types = self.query_resource_types()
        assert len(resource_types) == 4
        # ResourceTypes should be ordered by IDs.
        assert resource_types[0]["id"] == "1"
        assert resource_types[0]["name"] == "Exam"
        assert resource_types[1]["id"] == "2"
        assert resource_types[1]["name"] == "Exercise"
