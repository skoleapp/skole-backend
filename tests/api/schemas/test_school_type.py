from typing import List

from mypy.types import JsonDict

from tests.utils import BaseSchemaTestCase


class SchoolTypeSchemaTestCase(BaseSchemaTestCase):
    authenticated = True

    fields = """
    id
    name
    """

    def query_school_types(self) -> List[JsonDict]:
        query = f"""
          {{
            schoolTypes {{
              {self.fields}
            }}
          }}
        """
        return self.execute(query)["schoolTypes"]

    def query_school_type(self, id: int) -> JsonDict:
        variables = {"id": id}

        query = f"""
          query ($id: ID!) {{
            schoolType(id: $id) {{
              {self.fields}
            }}
          }}
        """
        return self.execute(query, variables=variables)["schoolType"]

    def test_query_school_types(self) -> None:
        school_types = self.query_school_types()
        assert len(school_types) == 3
        assert school_types[0]["id"] == "1"
        assert school_types[0]["name"] == "University"
        assert school_types[1]["id"] == "2"
        assert school_types[1]["name"] == "University of Applied Sciences"

    def test_query_school_type(self) -> None:
        # Test that every SchoolType from the list can be queried with its own id.
        school_types = self.query_school_types()
        for school_type in school_types:
            assert school_type == self.query_school_type(school_type["id"])

        # Test that returns None when ID not found.
        assert self.query_school_type(999) is None
