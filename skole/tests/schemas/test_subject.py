from typing import Optional

from skole.models import School
from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import JsonDict


class SubjectSchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    subject_fields = """
        fragment subjectFields on SubjectObjectType {
            id
            slug
            name
            courseCount
            resourceCount
        }
    """

    def query_subjects(
        self,
        *,
        school: str = "",
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
                $school: String,
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

    def query_autocomplete_subjects(self, *, name: str = "") -> list[JsonDict]:
        variables = {"name": name}

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
        return self.execute(graphql, variables=variables)

    def query_subject(self, *, slug: str) -> JsonDict:
        variables = {"slug": slug}

        # language=GraphQL
        graphql = (
            self.subject_fields
            + """
            query Subject($slug: String) {
                subject(slug: $slug) {
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
        school = "university-of-turku"
        res = self.query_subjects(school=school)
        school = School.objects.get(slug=school)
        school_subjects = school.subjects.values_list("id", flat=True)

        for subject in res["objects"]:
            assert int(subject["id"]) in school_subjects

    def test_autocomplete_subjects(self) -> None:
        subjects = self.query_autocomplete_subjects()

        assert len(subjects) == 4

        # Subjects are ordered alphabetically.
        assert subjects[0] == self.query_subject(slug="chemistry")
        assert subjects[1] == self.query_subject(slug="computer-engineering")
        assert subjects[2] == self.query_subject(slug="computer-science")

        # Query subjects by name.
        res = self.query_autocomplete_subjects(name="Computer")
        assert len(res) == 2
        assert res[0] == self.query_subject(slug="computer-engineering")
        assert res[1] == self.query_subject(slug="computer-science")

    def test_subject(self) -> None:
        slug = "computer-engineering"
        subject = self.query_subject(slug=slug)
        assert subject["id"] == "1"
        assert subject["slug"] == slug
        assert subject["name"] == "Computer Engineering"
        assert subject["courseCount"] == 22
        assert subject["resourceCount"] == 14
        assert self.query_subject(slug="not-found") is None
