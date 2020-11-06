from typing import List, Optional, cast

from skole.models import School
from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import ID, JsonDict


class SubjectSchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    subject_fields = """
        fragment subjectFields on SubjectObjectType {
            id
            name
            courseCount
            resourceCount
        }
    """

    def query_subjects(
        self,
        *,
        school: ID = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        assert_error: bool = False,
    ) -> JsonDict:
        variables = {
            "school": school,
            "pageSize": page_size,
            "page": page,
        }

        # language=GraphQL
        graphql = (
            self.subject_fields
            + """
            query Subjects (
                $school: ID,
                $page: Int,
                $pageSize: Int,
            ) {
                subjects (
                    school: $school,
                    page: $page,
                    pageSize: $pageSize,
                ) {
                    page
                    pages
                    hasNext
                    hasPrev
                    count
                    objects {
                        ...subjectFields
                    }
                }
            }
            """
        )

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def query_autocomplete_subjects(self, name: str = "") -> List[JsonDict]:
        # language=GraphQL
        graphql = (
            self.subject_fields
            + """
            query AutocompleteSubjects($name: String) {
                autocompleteSubjects(name: $name) {
                    ...subjectFields
                }
            }
            """
        )
        return cast(List[JsonDict], self.execute(graphql))

    def query_subject(self, *, id: ID) -> JsonDict:
        variables = {"id": id}

        # language=GraphQL
        graphql = (
            self.subject_fields
            + """
            query Subject($id: ID!) {
                subject(id: $id) {
                    ...subjectFields
                }
            }
            """
        )

        return self.execute(graphql, variables=variables)

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.subject_fields)

    def test_subjects(self) -> None:
        page_size = 10
        page = 1
        res = self.query_subjects(page=page, page_size=page_size)
        assert len(res["objects"]) == 4
        assert res["count"] == 4
        assert res["page"] == page
        assert res["hasNext"] is False
        assert res["hasPrev"] is False

        # Test that only subjects from a given school are returned.

        school_pk = 1
        school = School.objects.get(pk=school_pk)
        res = self.query_subjects(school=school_pk)
        school_subjects = school.subjects.values_list("id", flat=True)

        for subject in res["objects"]:
            assert int(subject["id"]) in school_subjects

    def test_autocomplete_subjects(self) -> None:
        subjects = self.query_autocomplete_subjects()

        # By default, subjects are ordered by the amount of courses.
        assert subjects[0] == self.query_subject(id=1)  # Most courses.
        assert subjects[1] == self.query_subject(id=2)  # 2nd most courses.
        assert subjects[2] == self.query_subject(id=3)  # 3rd most courses.

        # Query subjects by name.
        res = self.query_autocomplete_subjects("Computer")
        assert len(res) == 4
        assert res[0] == self.query_subject(id=1)  # Compututer Engineering.
        assert res[1] == self.query_subject(id=2)  # Computer Science.

        # TODO: Tests that no more than the maximum limit of results are returned.
        # Currently we don't have enough test schools to exceed the limit.

    def test_subject(self) -> None:
        subject = self.query_subject(id=1)
        assert subject["id"] == "1"
        assert subject["name"] == "Computer Engineering"
        assert subject["courseCount"] == 12
        assert subject["resourceCount"] == 4
        assert self.query_subject(id=999) is None
