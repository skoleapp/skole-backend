from typing import List, Optional, Sequence, cast

from skole.models import Course, User, Vote
from skole.tests.helpers import (
    SkoleSchemaTestCase,
    get_form_error,
    get_graphql_error,
    is_iso_datetime,
)
from skole.types import ID, CourseOrderingOption, JsonDict
from skole.utils.constants import GraphQLErrors, Messages, MutationErrors
from skole.utils.shortcuts import get_obj_or_none


class CourseSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    # language=GraphQL
    course_fields = """
        fragment courseFields on CourseObjectType {
            id
            name
            code
            subjects {
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
            score
            vote {
                status
            }
            starred
            created
            modified
        }
    """

    def query_autocomplete_courses(
        self, *, school: ID = None, name: str = ""
    ) -> List[JsonDict]:
        variables = {"school": school, "name": name}

        # language=GraphQL
        graphql = (
            self.course_fields
            + """
            query AutocompleteCourses($school: ID, $name: String) {
                autocompleteCourses(school: $school, name: $name) {
                    ...courseFields
                }
            }
            """
        )

        return cast(List[JsonDict], self.execute(graphql, variables=variables))

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
        assert_error: bool = False,
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
            query SearchCourses (
                $courseName: String, $courseCode: String, $subject: ID,
                $school: ID, $schoolType: ID, $country: ID,
                $city: ID, $page: Int, $pageSize: Int, $ordering: String
            ) {
                searchCourses(
                    courseName: $courseName, courseCode: $courseCode, subject: $subject,
                    school: $school, schoolType: $schoolType, country: $country,
                    city: $city, page: $page, pageSize: $pageSize, ordering: $ordering
                ) {
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

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def query_course(self, *, id: ID) -> JsonDict:
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

        return self.execute(graphql, variables=variables)

    def mutate_create_course(
        self,
        *,
        name: str = "test course",
        code: str = "code0001",
        subjects: Sequence[ID] = (1,),
        school: ID = 1,
        assert_error: bool = False,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="createCourse",
            input_type="CreateCourseMutationInput!",
            input={"name": name, "code": code, "subjects": subjects, "school": school},
            result="course { ...courseFields }",
            fragment=self.course_fields,
            assert_error=assert_error,
        )

    def mutate_delete_course(self, *, id: ID, assert_error: bool = False) -> JsonDict:
        return self.execute_input_mutation(
            name="deleteCourse",
            input_type="DeleteCourseMutationInput!",
            input={"id": id},
            result="message",
            assert_error=assert_error,
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.course_fields)

    def test_create_course(self) -> None:
        res = self.mutate_create_course()
        assert not res["errors"]
        course = res["course"]
        assert course["id"] == "16"
        assert course["name"] == "test course"
        assert course["code"] == "code0001"
        assert course["user"]["id"] == "2"

        # School is required.
        self.mutate_create_course(school=None, assert_error=True)

        # Subjects are not required.
        res = self.mutate_create_course(subjects=[])
        assert res["course"]["id"] == "17"

        # Can omit name but not code.
        res = self.mutate_create_course(code="")
        assert res["course"]["id"] == "18"
        res = self.mutate_create_course(name="")
        assert get_form_error(res) == "This field is required."
        assert res["course"] is None

        # Can't create one without logging in.
        self.authenticated_user = None
        res = self.mutate_create_course()
        assert res["errors"] == MutationErrors.AUTH_REQUIRED

    def test_delete_course(self) -> None:
        res = self.mutate_delete_course(id=1)
        assert res["message"] == Messages.COURSE_DELETED
        assert get_obj_or_none(Course, 1) is None

        # Can't delete the same course again.
        res = self.mutate_delete_course(id=1, assert_error=True)
        assert get_graphql_error(res) == "Course matching query does not exist."

        # Can't delete an other user's course.
        res = self.mutate_delete_course(id=2)
        assert res["errors"] == MutationErrors.NOT_OWNER

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
        assert self.query_search_courses() == self.query_search_courses(ordering="name")

        page_size = 4
        page = 1
        res = self.query_search_courses(page=page, page_size=page_size)
        assert len(res["objects"]) == page_size
        assert res["objects"][0] == self.query_course(id=1)
        assert res["objects"][1]["id"] == "10"
        assert res["count"] == 15
        assert res["page"] == page
        assert res["pages"] == 4
        assert res["hasNext"] is True
        assert res["hasPrev"] is False

        page = 2
        res = self.query_search_courses(page=page, page_size=page_size)
        assert res["objects"][0]["id"] == "13"
        assert res["objects"][1]["id"] == "14"
        assert len(res["objects"]) == page_size
        assert res["count"] == 15
        assert res["page"] == page
        assert res["pages"] == 4
        assert res["hasNext"] is True
        assert res["hasPrev"] is True

        page = 3
        res = self.query_search_courses(page=page, page_size=page_size)
        assert res["objects"][0]["id"] == "3"
        assert res["objects"][1]["id"] == "4"
        assert len(res["objects"]) == page_size
        assert res["count"] == 15
        assert res["page"] == page
        assert res["pages"] == 4
        assert res["hasNext"] is True
        assert res["hasPrev"] is True

        page = 4
        res = self.query_search_courses(page=page, page_size=page_size)
        assert res["objects"][0]["id"] == "7"
        assert res["objects"][1]["id"] == "8"
        assert len(res["objects"]) == 3  # Last page only has three results.
        assert res["count"] == 15
        assert res["page"] == page
        assert res["pages"] == 4
        assert res["hasNext"] is False
        assert res["hasPrev"] is True

        # The default sorting option is best first.
        res = self.query_search_courses()
        assert res == self.query_search_courses(ordering="best")
        assert res["objects"][0]["id"] == "1"
        assert res["objects"][-1]["id"] == "4"
        assert len(res["objects"]) == 10
        assert res["pages"] == 2

        res = self.query_search_courses(ordering="-name")
        assert res["objects"][0] == self.query_course(id=9)

        # Vote up one course, so it now has the most score.
        course = Course.objects.get(pk=7)
        user = User.objects.get(pk=2)
        vote, score = Vote.objects.perform_vote(user=user, status=1, target=course)
        res = self.query_search_courses(ordering="score")
        assert res["objects"][0]["id"] == str(course.pk)

        # Vote down one course, so it now has the least score.
        course = Course.objects.get(pk=3)
        user = User.objects.get(pk=2)
        vote, score = Vote.objects.perform_vote(user=user, status=-1, target=course)
        res = self.query_search_courses(ordering="score", page_size=20)
        assert res["objects"][-1]["id"] == str(course.pk)

        res = self.query_search_courses(course_name="Course 7")
        assert res["objects"][0]["id"] == "7"
        assert res["count"] == 1

        res = self.query_search_courses(course_code="0001")
        assert res["objects"][0]["id"] == "1"
        assert res["objects"][1]["id"] == "10"
        assert res["objects"][2]["id"] == "11"
        assert res["objects"][3]["id"] == "12"
        assert res["count"] == 7

        res = self.query_search_courses(country=1)
        assert res["count"] == 15

        res = self.query_search_courses(subject=1)
        assert res["count"] == 12

        res = self.query_search_courses(subject=2)
        assert res["count"] == 2

        res = self.query_search_courses(subject=999, school=999, country=999)
        assert res["count"] == 0

        res = self.query_search_courses(
            course_name="Test Engineering",
            course_code="2",
            subject=1,
            school=1,
            school_type=1,
            country=1,
            city=1,
            page=1,
            page_size=2,
            ordering="-name",
        )

        assert res["count"] == len(res["objects"]) == 2
        assert res["objects"][0]["code"] == "TEST0002"
        assert res["objects"][1]["code"] == "TEST00012"
        res = self.query_search_courses(ordering="badvalue", assert_error=True)  # type: ignore[arg-type]
        assert get_graphql_error(res) == GraphQLErrors.INVALID_ORDERING

    def test_autocomplete_courses(self) -> None:
        courses = self.query_autocomplete_courses()
        assert len(courses) == 15
        # By default, best courses are returned.
        assert courses[0] == self.query_course(id=1)  # Best
        assert courses[-1] == self.query_course(id=9)  # Worst

        # Query by course name
        assert self.query_autocomplete_courses(name="8")[0] == self.query_course(id=8)

        # TODO: Test that no more than the maximum limit of results are returned.
        # Currently we don't have enough test courses to exceed the limit.

    def test_course(self) -> None:
        course = self.query_course(id=1)
        assert course["id"] == "1"
        assert course["name"] == "Test Engineering Course 1"
        assert course["code"] == "TEST0001"
        assert course["subjects"] == [{"id": "1"}]
        assert course["school"] == {"id": "1"}
        assert course["user"] == {"id": "2"}
        assert is_iso_datetime(course["modified"])
        assert is_iso_datetime(course["created"])
        assert self.query_course(id=999) is None
