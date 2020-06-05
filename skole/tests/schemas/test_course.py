from typing import List, Optional

from mypy.types import JsonDict

from skole.models import Course, User, Vote
from skole.tests.helpers import SkoleSchemaTestCase, is_iso_datetime
from skole.utils.constants import GraphQLErrors
from skole.utils.types import ID, CourseOrderingOption


class CourseSchemaTests(SkoleSchemaTestCase):
    authenticated = True

    # language=GraphQL
    course_fields = """
        fragment courseFields on CourseObjectType {
            id
            name
            code
            subject {
                id
            }
            school {
                id
            }
            user {
                id
            }
            resources {
                id
            }
            comments {
                id
            }
            resourceCount
            score
            vote {
                status
            }
            starred
            created
            modified
        }
    """

    def query_search_courses(
        self,
        *,
        course_name: Optional[str] = None,
        course_code: Optional[str] = None,
        subject: ID = None,
        school: ID = None,
        school_type: ID = None,
        country: ID = None,
        city: ID = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        ordering: Optional[CourseOrderingOption] = None,
    ) -> JsonDict:
        variables = {
            "courseName": course_name,
            "courseCode": course_code,
            "subject": subject,
            "school": school,
            "schoolType": school_type,
            "country": country,
            "city": city,
            "page": page,
            "pageSize": page_size,
            "ordering": ordering,
        }
        # language=GraphQL
        graphql = (
            self.course_fields
            + """
            query SearchCourses($courseName: String, $courseCode: String, $subject: ID,
                                $school: ID, $schoolType: ID, $country: ID, $city: ID,
                                $page: Int, $pageSize: Int, $ordering: String) {
                searchCourses(courseName: $courseName, courseCode: $courseCode, subject: $subject,
                              school: $school, schoolType: $schoolType, country: $country, city: $city,
                              page: $page, pageSize: $pageSize, ordering: $ordering) {
                    page
                    pages
                    hasNext
                    hasPrev
                    objects {
                        ...courseFields
                    }
                    count
                }
            }
            """
        )
        res = self.execute(graphql, variables=variables)
        if self.should_error:
            return res
        return res["searchCourses"]

    def query_courses(self) -> List[JsonDict]:
        # language=GraphQL
        graphql = (
            self.course_fields
            + """
            query Courses {
                courses {
                    ...courseFields
                }
            }
            """
        )
        return self.execute(graphql)["courses"]

    def query_course(self, *, id: int) -> JsonDict:
        variables = {"id": id}

        # language=GraphQL
        graphql = (
            self.course_fields
            + """
            query Course($id: ID!) {
                course(id: $id) {
                    ...courseFields
                }
            }
            """
        )
        return self.execute(graphql, variables=variables)["course"]

    def test_field_fragment(self) -> None:
        self.authenticated = False
        self.assert_field_fragment_matches_schema(self.course_fields)

    def test_search_courses(self) -> None:
        # When searching courses the default ordering is by names, so the order will be:
        # Test Engineering Course 1
        # Test Engineering Course 10
        # Test Engineering Course 11
        # Test Engineering Course 12
        # Test Engineering Course 2
        # Test Engineering Course 3
        # ...
        # ...
        assert self.query_search_courses(ordering=None) == self.query_search_courses(
            ordering="name"
        )

        page_size = 4
        page = 1
        res = self.query_search_courses(page=page, page_size=page_size)
        assert len(res["objects"]) == page_size
        assert res["objects"][0] == self.query_course(id=1)
        assert res["objects"][1]["id"] == "10"
        assert res["count"] == 12
        assert res["page"] == page
        assert res["pages"] == 3
        assert res["hasNext"] is True
        assert res["hasPrev"] is False

        page = 2
        res = self.query_search_courses(page=page, page_size=page_size)
        assert res["objects"][0]["id"] == "2"
        assert res["objects"][1]["id"] == "3"
        assert len(res["objects"]) == page_size
        assert res["count"] == 12
        assert res["page"] == page
        assert res["pages"] == 3
        assert res["hasNext"] is True
        assert res["hasPrev"] is True

        page = 3
        res = self.query_search_courses(page=page, page_size=page_size)
        assert res["objects"][0]["id"] == "6"
        assert res["objects"][1]["id"] == "7"
        assert len(res["objects"]) == page_size
        assert res["count"] == 12
        assert res["page"] == page
        assert res["pages"] == 3
        assert res["hasNext"] is False
        assert res["hasPrev"] is True

        res = self.query_search_courses()
        assert res["objects"][0]["id"] == "1"
        assert res["objects"][-1]["id"] == "7"
        assert len(res["objects"]) == 10
        assert res["pages"] == 2

        res = self.query_search_courses(ordering="-name")
        assert res["objects"][0] == self.query_course(id=9)

        # Vote up one course, so it now has the most score.
        course = Course.objects.get(pk=7)
        user = User.objects.get(pk=2)
        vote, score = Vote.objects.perform_vote(user=user, status=1, target=course)
        res = self.query_search_courses(ordering="-score")
        assert res["objects"][0]["id"] == str(course.pk)

        # Vote down one course, so it now has the least score.
        course = Course.objects.get(pk=3)
        user = User.objects.get(pk=2)
        vote, score = Vote.objects.perform_vote(user=user, status=-1, target=course)
        res = self.query_search_courses(ordering="score")
        assert res["objects"][0]["id"] == str(course.pk)

        res = self.query_search_courses(course_name="Course 7")
        assert res["objects"][0]["id"] == "7"
        assert res["count"] == 1

        res = self.query_search_courses(course_code="0001")
        assert res["objects"][0]["id"] == "1"
        assert res["objects"][1]["id"] == "10"
        assert res["objects"][2]["id"] == "11"
        assert res["objects"][3]["id"] == "12"
        assert res["count"] == 4

        res = self.query_search_courses(country=1)
        assert res["count"] == 12

        res = self.query_search_courses(subject=1)
        assert res["count"] == 12

        res = self.query_search_courses(subject=2)
        assert res["count"] == 0

        res = self.query_search_courses(subject=999, school=999, country=999)
        assert res["count"] == 0

        self.should_error = True
        res = self.query_search_courses(ordering="badvalue")  # type: ignore[arg-type]
        assert res["errors"][0]["message"] == GraphQLErrors.INVALID_ORDERING

    def test_courses(self) -> None:
        courses = self.query_courses()
        assert len(courses) == 12
        # Courses should be ordered alphabetically.
        assert courses[0] == self.query_course(id=1)
        assert courses[0]["id"] == "1"
        assert courses[0]["name"] == "Test Engineering Course 1"
        assert courses[0]["code"] == "TEST0001"
        assert courses[1]["id"] == "10"
        assert courses[1]["name"] == "Test Engineering Course 10"
        assert courses[1]["code"] == "TEST00010"

    def test_course(self) -> None:
        course = self.query_course(id=1)
        assert course["id"] == "1"
        assert course["name"] == "Test Engineering Course 1"
        assert course["code"] == "TEST0001"
        assert course["subject"] == {"id": "1"}
        assert course["school"] == {"id": "1"}
        assert course["user"] == {"id": "2"}
        assert is_iso_datetime(course["modified"])
        assert is_iso_datetime(course["created"])

        assert self.query_course(id=999) is None
