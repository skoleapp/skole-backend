from collections.abc import Collection
from typing import Optional, cast

from skole.models import Course, User, Vote
from skole.tests.helpers import (
    SkoleSchemaTestCase,
    get_form_error,
    get_graphql_error,
    is_iso_datetime,
)
from skole.types import ID, CourseOrderingOption, JsonDict
from skole.utils.constants import GraphQLErrors, Messages, MutationErrors


class CourseSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    # language=GraphQL
    course_fields = """
        fragment courseFields on CourseObjectType {
            id
            name
            code
            score
            starCount
            resourceCount
            commentCount
            starred
            created
            modified
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
            vote {
                status
            }
        }
    """

    def query_autocomplete_courses(
        self, *, school: ID = None, name: str = ""
    ) -> list[JsonDict]:
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

        return cast(list[JsonDict], self.execute(graphql, variables=variables))

    def query_courses(
        self,
        *,
        course_name: Optional[str] = None,
        course_code: Optional[str] = None,
        subject: ID = None,
        school: ID = None,
        school_type: ID = None,
        country: ID = None,
        city: ID = None,
        user: ID = None,
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
            "user": user,
            "page": page,
            "pageSize": page_size,
            "ordering": ordering,
        }

        # language=GraphQL
        graphql = (
            self.course_fields
            + """
            query Courses (
                $courseName: String,
                $courseCode: String,
                $subject: ID,
                $school: ID,
                $schoolType: ID,
                $country: ID,
                $city: ID,
                $user: ID,
                $page: Int,
                $pageSize: Int,
                $ordering: String
            ) {
                courses(
                    courseName: $courseName,
                    courseCode: $courseCode,
                    subject: $subject,
                    school: $school,
                    schoolType: $schoolType,
                    country: $country,
                    city: $city,
                    user: $user,
                    page: $page,
                    pageSize: $pageSize,
                    ordering: $ordering
                ) {
                    page
                    pages
                    hasNext
                    hasPrev
                    count
                    objects {
                        ...courseFields
                    }
                }
            }
            """
        )

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def query_starred_courses(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        assert_error: bool = False,
    ) -> JsonDict:
        variables = {
            "page": page,
            "pageSize": page_size,
        }

        # language=GraphQL
        graphql = (
            self.course_fields
            + """
                query StarredCourses (
                    $page: Int,
                    $pageSize: Int
                ) {
                    starredCourses (
                        page: $page,
                        pageSize: $pageSize
                    ) {
                        page
                        pages
                        hasNext
                        hasPrev
                        count
                        objects {
                            ...courseFields
                        }
                    }
                }
            """
        )

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def query_suggested_courses(
        self,
        assert_error: bool = False,
    ) -> JsonDict:
        # language=GraphQL
        graphql = (
            self.course_fields
            + """
                query SuggestedCourses {
                    suggestedCourses {
                        ...courseFields
                    }
                }
            """
        )

        return self.execute(graphql, assert_error=assert_error)

    def query_suggested_courses_preview(
        self,
        assert_error: bool = False,
    ) -> JsonDict:
        # language=GraphQL
        graphql = (
            self.course_fields
            + """
                query SuggestedCoursesPreview {
                    suggestedCoursesPreview {
                        ...courseFields
                    }
                }
            """
        )

        return self.execute(graphql, assert_error=assert_error)

    def query_course(self, *, id: ID) -> JsonDict:
        variables = {"id": id}

        # language=GraphQL
        graphql = (
            self.course_fields
            + """
            query Course($id: ID) {
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
        subjects: Collection[ID] = (1,),
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
            result="successMessage",
            assert_error=assert_error,
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.course_fields)

    def test_create_course(self) -> None:
        res = self.mutate_create_course()
        assert not res["errors"]
        course = res["course"]
        assert course["id"] == "26"
        assert course["name"] == "test course"
        assert course["code"] == "code0001"
        assert course["user"]["id"] == "2"

        # These should be 0 by default.
        assert course["starCount"] == 0
        assert course["resourceCount"] == 0
        assert course["commentCount"] == 0

        # School is required.
        self.mutate_create_course(school=None, assert_error=True)

        # Subjects are not required.
        res = self.mutate_create_course(subjects=[])
        assert res["course"]["id"] == "27"

        # Can omit name but not code.
        res = self.mutate_create_course(code="")
        assert res["course"]["id"] == "28"
        res = self.mutate_create_course(name="")
        assert get_form_error(res) == "This field is required."
        assert res["course"] is None

        # Can't create one without logging in.
        self.authenticated_user = None
        res = self.mutate_create_course()
        assert res["errors"] == MutationErrors.AUTH_REQUIRED

    def test_delete_course(self) -> None:
        old_count = Course.objects.count()

        res = self.mutate_delete_course(id=1)
        assert res["successMessage"] == Messages.COURSE_DELETED
        assert Course.objects.get_or_none(pk=1) is None
        assert Course.objects.count() == old_count - 1

        # Can't delete the same course again.
        res = self.mutate_delete_course(id=1, assert_error=True)
        assert get_graphql_error(res) == "Course matching query does not exist."

        # Can't delete an other user's course.
        res = self.mutate_delete_course(id=2)
        assert res["errors"] == MutationErrors.NOT_OWNER

        assert Course.objects.count() == old_count - 1

    def test_courses(self) -> None:  # pylint: disable=too-many-statements
        # When searching courses the default ordering is `best`.
        assert self.query_courses() == self.query_courses(ordering="best")

        page_size = 4
        page = 1
        res = self.query_courses(page=page, page_size=page_size)
        assert len(res["objects"]) == page_size
        assert res["objects"][0] == self.query_course(id=1)
        assert res["objects"][1]["id"] == "2"
        assert res["count"] == 25
        assert res["page"] == page
        assert res["pages"] == 7
        assert res["hasNext"] is True
        assert res["hasPrev"] is False

        page = 2
        res = self.query_courses(page=page, page_size=page_size)
        assert res["objects"][0]["id"] == "5"
        assert res["objects"][1]["id"] == "6"
        assert len(res["objects"]) == page_size
        assert res["count"] == 25
        assert res["page"] == page
        assert res["pages"] == 7
        assert res["hasNext"] is True
        assert res["hasPrev"] is True

        page = 3
        res = self.query_courses(page=page, page_size=page_size)
        assert res["objects"][0]["id"] == "11"
        assert res["objects"][1]["id"] == "12"
        assert len(res["objects"]) == page_size
        assert res["count"] == 25
        assert res["page"] == page
        assert res["pages"] == 7
        assert res["hasNext"] is True
        assert res["hasPrev"] is True

        page = 7
        res = self.query_courses(page=page, page_size=page_size)
        assert res["objects"][0]["id"] == "9"
        assert len(res["objects"]) == 1  # Last page only has one result.
        assert res["count"] == 25
        assert res["page"] == page
        assert res["pages"] == 7
        assert res["hasNext"] is False
        assert res["hasPrev"] is True

        # The default sorting option is best first.
        res = self.query_courses()
        assert res == self.query_courses(ordering="best")
        assert res["objects"][0]["id"] == "1"
        assert res["objects"][-1]["id"] == "9"
        assert len(res["objects"]) == 25
        assert res["pages"] == 1

        res = self.query_courses(ordering="-name")
        assert res["objects"][0] == self.query_course(id=9)

        # Vote up one course, so it now has the most score.
        course = Course.objects.get(pk=7)
        user = User.objects.get(pk=2)
        Vote.objects.perform_vote(user=user, status=1, target=course)
        res = self.query_courses(ordering="score")
        assert res["objects"][0]["id"] == str(course.pk)

        # Vote down one course, so it now has the least score.
        course = Course.objects.get(pk=3)
        user = User.objects.get(pk=2)
        Vote.objects.perform_vote(user=user, status=-1, target=course)
        res = self.query_courses(ordering="score", page_size=25)
        assert res["objects"][-1]["id"] == str(course.pk)

        res = self.query_courses(course_name="Course 7")
        assert res["objects"][0]["id"] == "7"
        assert res["count"] == 1

        res = self.query_courses(course_code="0001")
        assert res["objects"][0]["id"] == "1"
        assert res["objects"][1]["id"] == "10"
        assert res["objects"][2]["id"] == "11"
        assert res["objects"][3]["id"] == "12"
        assert res["count"] == 11

        res = self.query_courses(country=1)
        assert res["count"] == 25

        res = self.query_courses(subject=1)
        assert res["count"] == 22

        res = self.query_courses(subject=2)
        assert res["count"] == 3

        res = self.query_courses(subject=999, school=999, country=999)
        assert res["count"] == 0

        res = self.query_courses(
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

        assert res["count"] == 8
        assert len(res["objects"]) == 2
        assert res["objects"][0]["code"] == "TEST00025"
        assert res["objects"][1]["code"] == "TEST00024"

        # Test that only courses of the correct user are returned.
        res = self.query_courses(user=self.authenticated_user)

        for course_obj in res["objects"]:
            assert int(course_obj["user"]["id"]) == self.authenticated_user

        # Test for some user that has created no courses.
        res = self.query_courses(user=10)
        assert len(res["objects"]) == 0
        assert res["count"] == 0

        # Test with invalid ordering.
        res = self.query_courses(ordering="badvalue", assert_error=True)  # type: ignore[arg-type]
        assert get_graphql_error(res) == GraphQLErrors.INVALID_ORDERING

    def test_autocomplete_courses(self) -> None:
        courses = self.query_autocomplete_courses()
        assert len(courses) == 25
        # By default, best courses are returned.
        assert courses[0] == self.query_course(id=1)  # Best
        assert courses[-1] == self.query_course(id=9)  # Worst

        # Query by course name
        assert self.query_autocomplete_courses(name="18")[0] == self.query_course(id=18)

    def test_starred_courses(self) -> None:
        page = 1
        page_size = 1

        res = self.query_starred_courses(page=page, page_size=page_size)
        assert len(res["objects"]) == page_size
        assert self.authenticated_user

        starred_courses = Course.objects.filter(
            stars__user__pk=self.authenticated_user
        ).values_list("id", flat=True)

        # Test that only courses starred by the user are returned.
        for course in res["objects"]:
            assert int(course["id"]) in starred_courses

        assert res["count"] == 2
        assert res["page"] == page
        assert res["pages"] == 2
        assert res["hasNext"] is True
        assert res["hasPrev"] is False

        page = 2

        res = self.query_starred_courses(page=page, page_size=page_size)
        assert len(res["objects"]) == page_size

        # Test that only courses starred by the user are returned.
        for course in res["objects"]:
            assert int(course["id"]) in starred_courses

        assert res["count"] == 2
        assert res["page"] == page
        assert res["pages"] == 2
        assert res["hasNext"] is False
        assert res["hasPrev"] is True

        # Shouldn't work without auth.
        self.authenticated_user = None

        res = self.query_starred_courses(
            page=page, page_size=page_size, assert_error=True
        )

        assert "permission" in get_graphql_error(res)
        assert res["data"] == {"starredCourses": None}

    def test_course(self) -> None:
        course = self.query_course(id=1)
        assert course["id"] == "1"
        assert course["name"] == "Test Engineering Course 1"
        assert course["code"] == "TEST0001"
        assert course["subjects"] == [{"id": "1"}, {"id": "2"}]
        assert course["school"] == {"id": "1"}
        assert course["user"] == {"id": "2"}
        assert course["starCount"] == 1
        assert course["resourceCount"] == 14
        assert course["commentCount"] == 18
        assert is_iso_datetime(course["modified"])
        assert is_iso_datetime(course["created"])
        assert self.query_course(id=999) is None
