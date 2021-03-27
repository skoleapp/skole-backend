from typing import Optional

from skole.models import Thread
from skole.tests.helpers import (
    TEST_IMAGE_PNG,
    FileData,
    SkoleSchemaTestCase,
    get_form_error,
    get_graphql_error,
    is_iso_datetime,
    open_as_file,
)
from skole.types import ID, JsonDict
from skole.utils.constants import GraphQLErrors, Messages, MutationErrors


class ThreadSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    # language=GraphQL
    thread_fields = """
        fragment threadFields on ThreadObjectType {
            id
            slug
            title
            score
            starCount
            commentCount
            starred
            created
            modified
            user {
                slug
            }
            comments {
                id
            }
            vote {
                status
            }
        }
    """

    def query_threads(
        self,
        *,
        search_term: Optional[str] = None,
        user: str = "",
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        assert_error: bool = False,
    ) -> JsonDict:
        variables = {
            "searchTerm": search_term,
            "user": user,
            "page": page,
            "pageSize": page_size,
        }

        # language=GraphQL
        graphql = (
            self.thread_fields
            + """
            query Threads (
                $searchTerm: String,
                $user: String,
                $page: Int,
                $pageSize: Int,
            ) {
                threads(
                    searchTerm: $searchTerm,
                    user: $user,
                    page: $page,
                    pageSize: $pageSize,
                ) {
                    page
                    pages
                    hasNext
                    hasPrev
                    count
                    objects {
                        ...threadFields
                    }
                }
            }
            """
        )

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def query_starred_threads(
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
            self.thread_fields
            + """
                query StarredThreads (
                    $page: Int,
                    $pageSize: Int
                ) {
                    starredThreads (
                        page: $page,
                        pageSize: $pageSize
                    ) {
                        page
                        pages
                        hasNext
                        hasPrev
                        count
                        objects {
                            ...threadFields
                        }
                    }
                }
            """
        )

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def query_suggested_threads(
        self,
        assert_error: bool = False,
    ) -> JsonDict:
        # language=GraphQL
        graphql = (
            self.thread_fields
            + """
                query SuggestedThreads {
                    suggestedThreads {
                        ...threadFields
                    }
                }
            """
        )

        return self.execute(graphql, assert_error=assert_error)

    def query_suggested_threads_preview(
        self,
        assert_error: bool = False,
    ) -> JsonDict:
        # language=GraphQL
        graphql = (
            self.thread_fields
            + """
                query SuggestedThreadsPreview {
                    suggestedThreadsPreview {
                        ...threadFields
                    }
                }
            """
        )

        return self.execute(graphql, assert_error=assert_error)

    def query_thread(self, *, slug: str) -> JsonDict:
        variables = {"slug": slug}

        # language=GraphQL
        graphql = (
            self.thread_fields
            + """
            query Thread($slug: String) {
                thread(slug: $slug) {
                    ...threadFields
                }
            }
            """
        )

        return self.execute(graphql, variables=variables)

    def mutate_create_thread(
        self,
        *,
        title: str = "test thread",
        text: str = "sample text",
        image: str = "",
        file_data: FileData = None,
        assert_error: bool = False,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="createThread",
            input_type="CreateThreadMutationInput!",
            input={
                "title": title,
                "text": text,
                "image": image,
            },
            result="thread { ...threadFields }",
            fragment=self.thread_fields,
            file_data=file_data,
            assert_error=assert_error,
        )

    def mutate_delete_thread(self, *, id: ID, assert_error: bool = False) -> JsonDict:
        return self.execute_input_mutation(
            name="deleteThread",
            input_type="DeleteThreadMutationInput!",
            input={"id": id},
            result="successMessage",
            assert_error=assert_error,
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.thread_fields)

    def test_create_thread(self) -> None:
        with open_as_file(TEST_IMAGE_PNG) as image:
            res = self.mutate_create_thread(file_data=[("image", image)])
            assert not res["errors"]
            thread = res["thread"]
            assert thread["id"] == "27"
            assert thread["title"] == "test thread"
            assert thread["user"]["slug"] == "testuser2"

        # These should be 0 by default.
        assert thread["starCount"] == 0
        assert thread["commentCount"] == 0

        # Title is required.
        res = self.mutate_create_thread(title="")
        assert get_form_error(res) == "This field is required."
        assert res["thread"] is None

        # Can't create one without logging in.
        self.authenticated_user = None
        res = self.mutate_create_thread()
        assert res["errors"] == MutationErrors.AUTH_REQUIRED

    def test_delete_thread(self) -> None:
        old_count = Thread.objects.count()
        res = self.mutate_delete_thread(id=1)
        assert res["successMessage"] == Messages.THREAD_DELETED
        assert Thread.objects.get_or_none(pk=1) is None
        assert Thread.objects.count() == old_count - 1

        # Can't delete the same thread again.
        res = self.mutate_delete_thread(id=1, assert_error=True)
        assert get_graphql_error(res) == "Thread matching query does not exist."

        # Can't delete an other user's thread.
        res = self.mutate_delete_thread(id=2)
        assert res["errors"] == MutationErrors.NOT_OWNER

        assert Thread.objects.count() == old_count - 1

    def test_threads(self) -> None:
        # First page.
        page_size = 4
        page = 1
        res = self.query_threads(page=page, page_size=page_size)
        assert len(res["objects"]) == page_size
        assert res["objects"][0] == self.query_thread(slug="test-thread-1")
        assert res["objects"][1]["id"] == "2"
        assert res["count"] == 26
        assert res["page"] == page
        assert res["pages"] == 7
        assert res["hasNext"] is True
        assert res["hasPrev"] is False

        # Second page.
        page = 2
        res = self.query_threads(page=page, page_size=page_size)
        assert res["objects"][0]["id"] == "5"
        assert res["objects"][1]["id"] == "6"
        assert len(res["objects"]) == page_size
        assert res["count"] == 26
        assert res["page"] == page
        assert res["pages"] == 7
        assert res["hasNext"] is True
        assert res["hasPrev"] is True

        # Last page.
        page = 7
        res = self.query_threads(page=page, page_size=page_size)
        assert res["objects"][0]["id"] == "8"
        assert len(res["objects"]) == 2
        assert res["count"] == 26
        assert res["page"] == page
        assert res["pages"] == 7
        assert res["hasNext"] is False
        assert res["hasPrev"] is True

        # Search by title.
        res = self.query_threads(search_term="Test Thread 7")
        assert res["objects"][0]["id"] == "7"
        assert res["count"] == 1

        # Search by text.
        res = self.query_threads(search_term="Test thread 7 text.")
        assert res["objects"][0]["id"] == "7"
        assert res["count"] == 1

        # Test that only threads of the correct user are returned.

        user_slug = "testuser2"  # Slug for `self.authenticated_user`.
        res = self.query_threads(user=user_slug)

        for thread_obj in res["objects"]:
            assert thread_obj["user"]["slug"] == user_slug

        # Test for some user that has created no threads.
        res = self.query_threads(user="testuser10")
        assert len(res["objects"]) == 0
        assert res["count"] == 0

    def test_starred_threads(self) -> None:
        res = self.query_starred_threads()
        assert len(res["objects"])
        assert self.authenticated_user

        starred_threads = Thread.objects.filter(
            stars__user__pk=self.authenticated_user
        ).values_list("id", flat=True)

        # Test that only threads starred by the user are returned.
        for thread in res["objects"]:
            assert int(thread["id"]) in starred_threads

        assert res["count"] == 2
        assert res["page"] == 1
        assert res["pages"] == 1
        assert res["hasNext"] is False
        assert res["hasPrev"] is False

        # Shouldn't work without auth.
        self.authenticated_user = None
        res = self.query_starred_threads(assert_error=True)
        assert get_graphql_error(res) == GraphQLErrors.AUTH_REQUIRED
        assert res["data"] == {"starredThreads": None}

    def test_thread(self) -> None:
        slug = "test-thread-1"
        thread = self.query_thread(slug=slug)
        assert thread["id"] == "1"
        assert thread["title"] == "Test Thread 1"
        assert thread["slug"] == slug
        assert thread["user"] == {"slug": "testuser2"}
        assert thread["starCount"] == 1
        assert thread["commentCount"] == 18
        assert is_iso_datetime(thread["modified"])
        assert is_iso_datetime(thread["created"])
        assert self.query_thread(slug="not-found") is None
