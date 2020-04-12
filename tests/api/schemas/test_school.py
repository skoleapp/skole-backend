from typing import List

from mypy.types import JsonDict

from tests.utils import BaseSchemaTestCase


class SchoolSchemaTestCase(BaseSchemaTestCase):
    authenticated = True

    fields = """
    id
    name
    subjects {
      id
    }
    courses {
      id
    }
    subjectCount
    courseCount
    schoolType
    country
    city
    """

    def query_schools(self) -> List[JsonDict]:
        query = f"""
          {{
            schools {{
              {self.fields}
            }}
          }}
        """
        return self.execute(query)["schools"]

    def query_school(self, id: int) -> JsonDict:
        variables = {"id": id}

        query = f"""
          query ($id: ID!) {{
            school(id: $id) {{
              {self.fields}
            }}
          }}
        """
        return self.execute(query, variables=variables)["school"]

    def test_query_schools(self) -> None:
        schools = self.query_schools()
        assert len(schools) == 6
        assert schools[0]["id"] == "2"
        assert schools[0]["name"] == "Aalto University"
        assert schools[0]["schoolType"] == "University"
        assert schools[0]["city"] == "Espoo"
        assert schools[5]["id"] == "1"
        assert schools[5]["name"] == "University of Turku"
        assert schools[5]["schoolType"] == "University"
        assert schools[5]["city"] == "Turku"

    def test_query_school(self) -> None:
        # Test that every School from the list can be queried with its own id.
        schools = self.query_schools()
        for school in schools:
            assert school == self.query_school(school["id"])

        # Test that returns None when ID not found.
        assert self.query_school(999) is None
