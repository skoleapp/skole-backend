import datetime
from typing import Optional
from unittest import mock

import libmat2.pdf
from django.http import HttpResponse
from django.test import override_settings

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
        user: ID = None,
        course: ID = None,
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
                    $user: ID,
                    $course: ID,
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

    def query_resource(self, *, id: ID) -> JsonDict:
        # language=GraphQL
        graphql = (
            self.resource_fields
            + """
            query Resource($id: ID) {
                resource(id: $id) {
                    ...resourceFields
                }
            }
            """
        )

        return self.execute(graphql, variables={"id": id})

    def mutate_create_resource(
        self,
        *,
        title: str = "test title",
        file: str = "",
        resource_type: ID = 1,
        course: ID = 1,
        date: Optional[datetime.datetime] = None,
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
        date: Optional[datetime.datetime] = None,
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

        res = self.query_resources(
            user=self.authenticated_user, page=page, page_size=page_size
        )

        assert len(res["objects"]) == page_size

        for course in res["objects"]:
            assert int(course["user"]["id"]) == self.authenticated_user

        assert res["count"] == 12
        assert res["page"] == page
        assert res["pages"] == 12
        assert res["hasNext"] is True
        assert res["hasPrev"] is False

        # Test for some user that has created no resources.

        page = 1
        res = self.query_resources(user=9, page=page, page_size=page_size)
        assert res["count"] == 0
        assert res["page"] == page
        assert res["pages"] == 1
        assert res["hasNext"] is False
        assert res["hasPrev"] is False

        # Test that only resources of the correct course are returned.

        page = 14
        course_pk = "1"

        res = self.query_resources(course=course_pk, page=page, page_size=page_size)

        assert len(res["objects"]) == page_size

        for resource in res["objects"]:
            assert resource["course"]["id"] == course_pk

        assert res["count"] == 14
        assert res["page"] == page
        assert res["pages"] == 14
        assert res["hasNext"] is False
        assert res["hasPrev"] is True

        # Test for some course that has no courses.

        page = 1
        res = self.query_resources(course=9, page=page, page_size=page_size)
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
            resource = self.query_resource(id=1)
            assert resource["id"] == "1"
            assert resource["title"] == "Sample Exam 1"
            assert resource["file"] == "/media/uploads/resources/test_resource.pdf"
            assert resource["course"]["id"] == "1"
            assert resource["starCount"] == 1
            assert resource["commentCount"] == 4
            assert resource["downloads"] == 0
            assert self.client.get(resource["file"]).status_code == 200

        assert self.query_resource(id=999) is None

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
        assert resource["id"] == "15"
        assert resource["title"] == "test title"
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
