from typing import Optional

from skole.models import Comment, Thread
from skole.tests.helpers import (
    TEST_IMAGE_PNG,
    UPLOADED_IMAGE_PNG,
    FileData,
    SkoleSchemaTestCase,
    get_form_error,
    get_graphql_error,
    get_last,
    is_slug_match,
    open_as_file,
)
from skole.types import ID, JsonDict
from skole.utils.constants import Errors, Messages

_comment_fields = """
    fragment _commentFields on CommentObjectType {
        id
        text
        image
        imageThumbnail
        file
        score
        replyCount
        isOwn
        created
        modified
        user {
            id
            slug
            username
            avatarThumbnail
        }
        thread {
            slug
            title
        }
        vote {
            id
            status
        }
    }
"""


class CommentSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    # language=GraphQL
    comment_fields = (
        _comment_fields
        + """
        fragment commentFields on CommentObjectType {
            ..._commentFields
            replyComments {
                ..._commentFields
            }
            comment {
                ..._commentFields
            }
        }
        """
    )

    def query_comments(
        self,
        *,
        user: str = "",
        thread: str = "",
        ordering: str = "best",
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        assert_error: bool = False,
    ) -> JsonDict:
        variables = {
            "user": user,
            "thread": thread,
            "ordering": ordering,
            "page": page,
            "pageSize": page_size,
        }

        # language=GraphQL
        graphql = (
            self.comment_fields
            + """
                query Comments (
                    $user: String,
                    $thread: String,
                    $ordering: String,
                    $page: Int,
                    $pageSize: Int
                ) {
                    comments (
                        user: $user,
                        thread: $thread,
                        ordering: $ordering,
                        page: $page,
                        pageSize: $pageSize
                    ) {
                        page
                        pages
                        hasNext
                        hasPrev
                        count
                        objects {
                            ...commentFields
                        }
                    }
                }
            """
        )

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def mutate_create_comment(
        self,
        *,
        user: ID = 2,
        text: str = "",
        file: str = "",
        image: str = "",
        thread: ID = None,
        comment: ID = None,
        file_data: FileData = None,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="createComment",
            input_type="CreateCommentMutationInput!",
            input={
                "user": user,
                "text": text,
                "file": file,
                "image": image,
                "thread": thread,
                "comment": comment,
            },
            result="comment { ...commentFields }",
            fragment=self.comment_fields,
            file_data=file_data,
        )

    def mutate_update_comment(
        self,
        *,
        id: ID,
        text: str = "",
        file: str = "",
        image: str = "",
        file_data: FileData = None,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="updateComment",
            input_type="UpdateCommentMutationInput!",
            input={"id": id, "text": text, "file": file, "image": image},
            result="comment { ...commentFields }",
            fragment=self.comment_fields,
            file_data=file_data,
        )

    def mutate_delete_comment(self, *, id: ID, assert_error: bool = False) -> JsonDict:
        return self.execute_input_mutation(
            name="deleteComment",
            input_type="DeleteCommentMutationInput!",
            input={"id": id},
            result="successMessage",
            assert_error=assert_error,
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.comment_fields)

    def test_create_comment(self) -> None:
        # Create a reply comment.
        old_count = Comment.objects.count()
        text = "Some text for the comment."
        res = self.mutate_create_comment(text=text, comment=2)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 1
        assert Comment.objects.get(pk=2).reply_comments.count() == 1
        assert Comment.objects.get(pk=2).reply_comments.get().text == text
        assert Comment.objects.get(pk=2).reply_comments.get().pk == int(comment["id"])
        assert comment["user"]["id"] == "2"

        # Create a comment to a thread.
        res = self.mutate_create_comment(text=text, thread=2)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 2
        assert Thread.objects.get(pk=2).comments.count() == 2
        assert get_last(Thread.objects.get(pk=2).comments).text == text
        assert get_last(Thread.objects.get(pk=2).comments).pk == int(comment["id"])

        # Create a comment with an image.
        with open_as_file(TEST_IMAGE_PNG) as image:
            res = self.mutate_create_comment(
                text=text, thread=2, file_data=[("image", image)]
            )

        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert is_slug_match(UPLOADED_IMAGE_PNG, comment["image"])
        assert comment["imageThumbnail"]
        assert Comment.objects.count() == old_count + 3

        # Test creating anonymous comment as authenticated user.
        res = self.mutate_create_comment(user=None, text=text, thread=2)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["user"] is None
        assert comment["isOwn"] is True
        assert Comment.objects.count() == old_count + 4

        # Can't spoof the comment author.
        res = self.mutate_create_comment(user=3, text=text, thread=2)
        assert get_form_error(res) == Errors.INVALID_COMMENT_AUTHOR
        assert not res["comment"]

        # Can't create a comment with no text and no image.
        res = self.mutate_create_comment(text="", image="", thread=1)
        assert get_form_error(res) == Errors.COMMENT_EMPTY
        assert not res["comment"]

        # Can't create a comment without being verified.
        self.authenticated_user = 3
        res = self.mutate_create_comment(text=text, thread=3)
        assert get_form_error(res) == Errors.VERIFICATION_REQUIRED
        assert not res["comment"]

        # Can't a comment without logging in
        self.authenticated_user = None
        res = self.mutate_create_comment(text=text, thread=3)
        assert get_form_error(res) == Errors.AUTH_REQUIRED
        assert not res["comment"]

        # Check that the comment count hasn't changed.
        assert Comment.objects.count() == old_count + 4

    def test_update_comment(self) -> None:
        new_text = "some new text"

        # Update comment with new text and image.
        with open_as_file(TEST_IMAGE_PNG) as image:
            res = self.mutate_update_comment(
                id=4,
                text=new_text,
                image="",
                file_data=[("image", image)],
            )

        assert not res["errors"]
        assert is_slug_match(UPLOADED_IMAGE_PNG, res["comment"]["image"])
        assert res["comment"]["text"] == new_text
        assert res["comment"]["thread"]["slug"] == "test-thread-1"
        assert res["comment"]["comment"] is None

        # Clear image from comment.
        comment = Comment.objects.get(pk=1)
        assert comment.image
        res = self.mutate_update_comment(id=1, text=comment.text, image="")
        assert res["comment"]["image"] == ""
        assert not Comment.objects.get(pk=1).image

        # Can't update someone else's comment.
        res = self.mutate_update_comment(id=2, text=new_text)
        assert get_form_error(res) == Errors.NOT_OWNER

        # Can't update a comment to have no text and no image.
        res = self.mutate_update_comment(id=1, text="", image="")
        assert res["errors"] is not None
        assert res["comment"] is None

        # Can't update a comment when not verified.
        user = self.get_authenticated_user()
        user.verified = False
        user.save()
        res = self.mutate_update_comment(id=1, text=new_text)
        assert get_form_error(res) == Errors.VERIFICATION_REQUIRED
        assert not res["comment"]

        # Can't update a comment when not logged in.
        self.authenticated_user = None
        res = self.mutate_update_comment(id=1, text=new_text)
        assert get_form_error(res) == Errors.AUTH_REQUIRED
        assert not res["comment"]

    def test_delete_comment(self) -> None:
        old_count = Comment.objects.count()

        assert Comment.objects.filter(pk=1)
        res = self.mutate_delete_comment(id=1)
        assert res["successMessage"] == Messages.COMMENT_DELETED
        assert not Comment.objects.filter(pk=1)
        assert Comment.objects.count() == old_count - 1

        res = self.mutate_delete_comment(id=1, assert_error=True)
        assert get_graphql_error(res) == "Comment matching query does not exist."

        res = self.mutate_delete_comment(id=2)
        assert get_form_error(res) == Errors.NOT_OWNER

        assert Comment.objects.count() == old_count - 1

    def test_comments(self) -> None:
        page = 1
        page_size = 1

        # Test that only comments of the correct user are returned.

        user = "testuser2"  # Slug for `self.authenticated_user`.

        res = self.query_comments(user=user, page=page, page_size=page_size)

        assert len(res["objects"]) == page_size

        for comment in res["objects"]:
            assert int(comment["user"]["id"]) == self.authenticated_user
            assert comment["isOwn"] is True

        assert res["count"] == 14
        assert res["page"] == page
        assert res["pages"] == 14
        assert res["hasNext"] is True
        assert res["hasPrev"] is False

        # Test querying another user's comments.
        res = self.query_comments(user="testuser9", page=page, page_size=page_size)
        for comment in res["objects"]:
            assert comment["user"]["id"] == "9"
            assert comment["isOwn"] is False

        # Test for some user that has created no comments.
        page = 1
        res = self.query_comments(user="testuser10", page=page, page_size=page_size)
        assert res["count"] == 0
        assert res["page"] == page
        assert res["pages"] == 1
        assert res["hasNext"] is False
        assert res["hasPrev"] is False

        # TODO: Test thread comments.
        # TODO: Test ordering.
