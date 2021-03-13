import datetime
from typing import Optional
from unittest import mock

import libmat2.pdf
from django.http import HttpResponse
from django.test import override_settings
from django.utils import timezone

from skole.models import Author, Resource
from skole.tests.helpers import (
    TEST_ATTACHMENT_PNG,
    TEST_RESOURCE_PDF,
    UPLOADED_RESOURCE_PDF,
    FileData,
    SkoleSchemaTestCase,
    get_form_error,
    get_graphql_error,
    is_slug_match,
    open_as_file,
)
from skole.types import ID, JsonDict
from skole.utils.constants import Messages, MutationErrors, ValidationErrors


class ResourceSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    # language=GraphQL
    resource_fields = """
        fragment resourceFields on ResourceObjectType {
            id
            slug
            title
            file
            date
            downloads
            score
            starred
            starCount
            commentCount
            modified
            created
            resourceType {
                id
                name
            }
            user {
                id
                slug
            }
            author {
                id
                name
                user {
                    id
                }
            }
            course {
                id
                slug
            }
            comments {
                id
            }
            school {
                id
            }
            vote {
                id
                status
            }
        }
    """

    def query_resources(
        self,
        *,
        user: str = "",
        course: str = "",
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        assert_error: bool = False,
    ) -> JsonDict:
        variables = {
            "user": user,
            "course": course,
            "page": page,
            "pageSize": page_size,
        }

        # language=GraphQL
        graphql = (
            self.resource_fields
            + """
                query Resources (
                    $user: String,
                    $course: String,
                    $page: Int,
                    $pageSize: Int
                ) {
                    resources (
                        user: $user,
                        course: $course,
                        page: $page,
                        pageSize: $pageSize
                    ) {
                        page
                        pages
                        hasNext
                        hasPrev
                        count
                        objects {
                            ...resourceFields
                        }
                    }
                }
            """
        )

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def query_starred_resources(
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
            self.resource_fields
            + """
                query StarredResources (
                    $page: Int,
                    $pageSize: Int
                ) {
                    starredResources (
                        page: $page,
                        pageSize: $pageSize
                    ) {
                        page
                        pages
                        hasNext
                        hasPrev
                        count
                        objects {
                            ...resourceFields
                        }
                    }
                }
            """
        )

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def query_resource(self, *, slug: str) -> JsonDict:
        variables = {"slug": slug}

        # language=GraphQL
        graphql = (
            self.resource_fields
            + """
            query Resource($slug: String) {
                resource(slug: $slug) {
                    ...resourceFields
                }
            }
            """
        )

        return self.execute(graphql, variables=variables)

    def mutate_create_resource(
        self,
        *,
        title: str = "test title",
        file: str = "",
        resource_type: ID = 1,
        course: ID = 1,
        date: Optional[datetime.date] = None,
        author: Optional[str] = None,
        file_data: FileData = None,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="createResource",
            input_type="CreateResourceMutationInput!",
            input={
                "title": title,
                "file": file,
                "resourceType": resource_type,
                "course": course,
                "date": date,
                "author": author,
            },
            result="resource { ...resourceFields }",
            fragment=self.resource_fields,
            file_data=file_data,
        )

    def mutate_update_resource(
        self,
        *,
        id: ID = 1,
        title: str = "test title",
        resource_type: ID = 1,
        date: Optional[datetime.date] = None,
        author: Optional[str] = None,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="updateResource",
            input_type="UpdateResourceMutationInput!",
            input={
                "id": id,
                "title": title,
                "resourceType": resource_type,
                "date": date,
                "author": author,
            },
            result="resource { ...resourceFields }",
            fragment=self.resource_fields,
        )

    def mutate_download_resource(
        self,
        *,
        id: ID = 1,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="downloadResource",
            input_type="DownloadResourceMutationInput!",
            input={
                "id": id,
            },
            result="resource { ...resourceFields } successMessage",
            fragment=self.resource_fields,
        )

    def mutate_delete_resource(self, *, id: ID, assert_error: bool = False) -> JsonDict:
        return self.execute_input_mutation(
            name="deleteResource",
            input_type="DeleteResourceMutationInput!",
            input={"id": id},
            result="successMessage",
            assert_error=assert_error,
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.resource_fields)

    def test_resources(self) -> None:
        page = 1
        page_size = 1

        # Test that only resources of the correct user are returned.

        user = "testuser2"  # Slug for `self.authenticated_user`.

        res = self.query_resources(user=user, page=page, page_size=page_size)

        assert len(res["objects"]) == page_size

        for resource in res["objects"]:
            assert resource["user"]["slug"] == user

        assert res["count"] == 12
        assert res["page"] == page
        assert res["pages"] == 12
        assert res["hasNext"] is True
        assert res["hasPrev"] is False

        # Test for some user that has created no resources.

        page = 1
        res = self.query_resources(user="testuser9", page=page, page_size=page_size)
        assert res["count"] == 0
        assert res["page"] == page
        assert res["pages"] == 1
        assert res["hasNext"] is False
        assert res["hasPrev"] is False

        # Test that only resources of the correct course are returned.

        page = 15
        course = "test-engineering-course-1-test0001"

        res = self.query_resources(course=course, page=page, page_size=page_size)

        assert len(res["objects"]) == page_size

        for resource in res["objects"]:
            assert resource["course"]["slug"] == course

        assert res["count"] == 15
        assert res["page"] == page
        assert res["pages"] == 15
        assert res["hasNext"] is False
        assert res["hasPrev"] is True

        # Test for some course that has no resources.

        page = 1

        res = self.query_resources(
            course="test-engineering-course-9-test0009",
            page=page,
            page_size=page_size,
        )

        assert res["count"] == 0
        assert res["page"] == page
        assert res["pages"] == 1
        assert res["hasNext"] is False
        assert res["hasPrev"] is False

    def test_starred_resources(self) -> None:
        page = 1
        page_size = 1

        res = self.query_starred_resources(page=page, page_size=page_size)
        assert len(res["objects"]) == page_size
        assert self.authenticated_user

        starred_resources = Resource.objects.filter(
            stars__user__pk=self.authenticated_user
        ).values_list("id", flat=True)

        # Test that only resources starred by the user are returned.
        for resource in res["objects"]:
            assert int(resource["id"]) in starred_resources

        assert res["count"] == 2
        assert res["page"] == page
        assert res["pages"] == 2
        assert res["hasNext"] is True
        assert res["hasPrev"] is False

        page = 2

        res = self.query_starred_resources(page=page, page_size=page_size)
        assert len(res["objects"]) == page_size

        # Test that only resources starred by the user are returned.
        for resource in res["objects"]:
            assert int(resource["id"]) in starred_resources

        assert res["count"] == 2
        assert res["page"] == page
        assert res["pages"] == 2
        assert res["hasNext"] is False
        assert res["hasPrev"] is True

        # Shouldn't work without auth.
        self.authenticated_user = None

        res = self.query_starred_resources(
            page=page, page_size=page_size, assert_error=True
        )

        assert "permission" in get_graphql_error(res)
        assert res["data"] == {"starredResources": None}

    def test_resource(self) -> None:
        with override_settings(DEBUG=True):  # To access media.
            slug = "sample-exam-1-2012-12-12"
            resource = self.query_resource(slug=slug)
            assert resource["id"] == "1"
            assert resource["title"] == "Sample Exam 1"
            assert resource["date"] == "2012-12-12"
            assert resource["slug"] == slug
            assert resource["file"] == "/media/uploads/resources/test_resource.pdf"
            assert resource["course"]["id"] == "1"
            assert resource["starCount"] == 1
            assert resource["commentCount"] == 4
            assert resource["downloads"] == 0
            assert self.client.get(resource["file"]).status_code == 200

        assert self.query_resource(slug="not-found") is None

    def test_create_resource_ok(self) -> None:  # pylint: disable=too-many-statements
        # Create a resource with a PDF file.
        with mock.patch(
            target="libmat2.pdf.PDFParser.remove_all",
            side_effect=libmat2.pdf.PDFParser.remove_all,
            autospec=True,  # To correctly pass `self` to the mocked method.
        ) as mocked:
            with open_as_file(TEST_RESOURCE_PDF) as file:
                res = self.mutate_create_resource(file_data=[("file", file)])
                mocked.assert_called()

        resource = res["resource"]
        assert not res["errors"]
        assert resource["id"] == "16"
        assert resource["title"] == "test title"
        current_date = str(datetime.date.today())
        assert resource["date"] == current_date
        assert resource["slug"] == f"test-title-{current_date}"
        assert resource["author"] is None
        assert is_slug_match(UPLOADED_RESOURCE_PDF, resource["file"])

        # These should be 0 by default.
        assert resource["starCount"] == 0
        assert resource["commentCount"] == 0
        assert resource["downloads"] == 0

        # Create a resource with PNG file that will get converted to a PDF.
        with open_as_file(TEST_RESOURCE_PDF) as file:
            response = HttpResponse(content=file.read())
        with override_settings(CLOUDMERSIVE_API_KEY="xxx"):
            with mock.patch("requests.post", return_value=response):
                with open_as_file(TEST_ATTACHMENT_PNG) as file:
                    res = self.mutate_create_resource(file_data=[("file", file)])

        resource = res["resource"]
        assert not res["errors"]

        # Set the date to the current day.
        with open_as_file(TEST_RESOURCE_PDF) as file:
            date = timezone.localdate()
            res = self.mutate_create_resource(date=date, file_data=[("file", file)])
            resource = res["resource"]
            assert not res["errors"]
            assert resource["date"] is not None
            assert resource["date"] == date.isoformat()

        author_count = Author.objects.count()

        # Create a resource with the author set.
        with open_as_file(TEST_RESOURCE_PDF) as file:
            author = "Some Guy"
            res = self.mutate_create_resource(author=author, file_data=[("file", file)])
            resource = res["resource"]
            assert not res["errors"]
            assert resource["author"]["id"] == "1"
            assert resource["author"]["name"] == author
            assert resource["author"]["user"] is None
            assert Author.objects.count() == author_count + 1

        # Should reuse the same Author model instance for same names.
        with open_as_file(TEST_RESOURCE_PDF) as file:
            res = self.mutate_create_resource(author=author, file_data=[("file", file)])
            resource = res["resource"]
            assert not res["errors"]
            assert resource["author"]["name"] == author
            assert resource["author"]["user"] is None
            assert Author.objects.count() == author_count + 1

        # Different name should get a new Author ID.
        with open_as_file(TEST_RESOURCE_PDF) as file:
            author = "Other Guy"
            res = self.mutate_create_resource(author=author, file_data=[("file", file)])
            resource = res["resource"]
            assert not res["errors"]
            assert resource["author"]["name"] == author
            assert resource["author"]["user"] is None
            assert Author.objects.count() == author_count + 2

        # If the author is set to a user's username it links to it.
        with open_as_file(TEST_RESOURCE_PDF) as file:
            author = self.get_authenticated_user().username
            res = self.mutate_create_resource(author=author, file_data=[("file", file)])
            resource = res["resource"]
            assert not res["errors"]
            assert resource["author"]["name"] == ""
            assert resource["author"]["user"]["id"] == "2"

    def test_create_resource_error(self) -> None:
        # Can't create a resource with no file.
        res = self.mutate_create_resource()
        assert res["resource"] is None
        assert get_form_error(res) == "This field is required."
        res = self.mutate_create_resource(file="foo")
        assert res["resource"] is None
        assert get_form_error(res) == "This field is required."

        # Can't create one without logging in.
        self.authenticated_user = None
        res = self.mutate_create_resource()
        assert res["errors"] == MutationErrors.AUTH_REQUIRED

        # The date cannot be in the future.
        with open_as_file(TEST_RESOURCE_PDF) as file:
            self.authenticated_user = 2
            date = timezone.localdate() + datetime.timedelta(days=2)
            res = self.mutate_create_resource(date=date, file_data=[("file", file)])
            assert "future" in get_form_error(res)

    def test_update_resource(self) -> None:
        new_title = "new title"
        new_resource_type = 3

        res = self.mutate_update_resource(
            title=new_title, resource_type=new_resource_type
        )

        resource = res["resource"]
        assert not res["errors"]
        assert resource["title"] == new_title
        assert resource["resourceType"]["name"] == "Exam"
        assert resource["date"] == "2012-12-12"
        assert resource["slug"] == "sample-exam-1-2012-12-12"  # Slugs are immutable.

        # Set the date to the current day.
        date = timezone.localdate()
        res = self.mutate_update_resource(date=date)
        resource = res["resource"]
        assert not res["errors"]
        assert resource["date"] is not None
        assert resource["date"] == date.isoformat()

        # Set the author.
        author = "New Guy"
        res = self.mutate_update_resource(
            title=new_title,
            resource_type=new_resource_type,
            author=author,
        )
        resource = res["resource"]
        assert not res["errors"]
        assert resource["author"]["name"] == author
        assert resource["author"]["user"] is None

        # If the author is set to a user's username it links to it.
        author = "testuser4"
        res = self.mutate_update_resource(
            title=new_title,
            resource_type=new_resource_type,
            author=author,
        )
        resource = res["resource"]
        assert not res["errors"]
        assert resource["author"]["name"] == ""
        assert resource["author"]["user"]["id"] == "4"

        # Can't update someone else's resource.
        res = self.mutate_update_resource(id=2)
        assert get_form_error(res) == ValidationErrors.NOT_OWNER
        assert res["resource"] is None

        # The date cannot be in the future.
        date = timezone.localdate() + datetime.timedelta(days=2)
        res = self.mutate_update_resource(date=date)
        assert "future" in get_form_error(res)

    def test_delete_resource(self) -> None:
        old_count = Resource.objects.count()

        res = self.mutate_delete_resource(id=1)
        assert res["successMessage"] == Messages.RESOURCE_DELETED
        assert Resource.objects.get_or_none(pk=1) is None
        assert Resource.objects.count() == old_count - 1

        # Can't delete the same resource again.
        res = self.mutate_delete_resource(id=1, assert_error=True)
        assert get_graphql_error(res) == "Resource matching query does not exist."

        # Can't delete an other user's resource.
        res = self.mutate_delete_resource(id=2)
        assert res["errors"] == MutationErrors.NOT_OWNER

        assert Resource.objects.count() == old_count - 1

    def test_download_resource(self) -> None:
        resource = Resource.objects.get(pk=1)
        assert resource.downloads == 0

        res = self.mutate_download_resource(id=resource.pk)

        resource = res["resource"]
        assert not res["errors"]
        assert res["resource"]["downloads"] == 1
