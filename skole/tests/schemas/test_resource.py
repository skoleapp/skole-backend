import datetime
from typing import Optional
from unittest import mock

import requests
from django.http import HttpResponse
from django.test import override_settings

from skole.tests.helpers import (
    FileData,
    SkoleSchemaTestCase,
    get_form_error,
    is_slug_match,
    open_as_file,
)
from skole.types import ID, JsonDict
from skole.utils.constants import MutationErrors, ValidationErrors


class ResourceSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    # language=GraphQL
    resource_fields = """
        fragment resourceFields on ResourceObjectType {
            id
            title
            file
            resourceType
            date
            downloads
            score
            starred
            user {
                id
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
            modified
            created
        }
    """

    def query_resource(self, *, id: ID) -> JsonDict:
        # language=GraphQL
        graphql = (
            self.resource_fields
            + """
            query Resource($id: ID!) {
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
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="updateResource",
            input_type="UpdateResourceMutationInput!",
            input={
                "id": id,
                "title": title,
                "resourceType": resource_type,
                "date": date,
            },
            result="resource { ...resourceFields }",
            fragment=self.resource_fields,
        )

    def mutate_delete_resource(self, *, id: ID, assert_error: bool = False) -> JsonDict:
        return self.execute_input_mutation(
            name="deleteResource",
            input_type="DeleteResourceMutationInput!",
            input={"id": id},
            result="message",
            assert_error=assert_error,
        )

    def test_resource(self) -> None:
        with override_settings(DEBUG=True):  # To access media.
            resource = self.query_resource(id=1)
            assert resource["id"] == "1"
            assert resource["title"] == "Sample exam 1"
            assert resource["file"] == "/media/uploads/resources/test_resource.pdf"
            assert resource["course"]["id"] == "1"
            assert self.client.get(resource["file"]).status_code == 200

        assert self.query_resource(id=999) is None

    def test_create_resource(self) -> None:
        pdf_file_path = "media/uploads/resources/test_resource.pdf"
        png_file_path = "media/uploads/attachments/test_attachment.png"

        # Create a resource with a PDF file.
        with open_as_file(pdf_file_path) as file:
            res = self.mutate_create_resource(file_data=[("file", file)])
        resource = res["resource"]
        assert not res["errors"]
        assert resource["id"] == "4"
        assert resource["title"] == "test title"
        assert is_slug_match(pdf_file_path, resource["file"])

        # Create a resource with PNG file that will get converted to a PDF.
        with open_as_file(pdf_file_path) as file:
            response = HttpResponse(content=file.read())
        with override_settings(CLOUDMERSIVE_API_KEY="xxx"):
            with mock.patch.object(requests, "post", return_value=response):
                with open_as_file(png_file_path) as file:
                    res = self.mutate_create_resource(file_data=[("file", file)])
        resource = res["resource"]
        assert not res["errors"]
        assert resource["id"] == "5"
        assert is_slug_match(
            "/media/uploads/resources/test_attachment.pdf", resource["file"]
        )

        # Can't create a resource with no file.
        res = self.mutate_create_resource()
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
        assert resource["resourceType"] == "Note"
        assert resource["date"] == "2012-12-12"

        # Can't update someone else's resource.
        res = self.mutate_update_resource(id=2)
        assert get_form_error(res) == ValidationErrors.NOT_OWNER
        assert res["resource"] is None

    def test_delete_resource(self) -> None:
        pass
