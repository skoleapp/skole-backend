from django.conf import settings

from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import ID, JsonDict


class SuggestionSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    # language=GraphQL
    suggestion_fields = """
        fragment suggestionFields on SuggestionsUnion {
            ... on CourseObjectType {
                id
                name
                code
                score
                starCount
                resourceCount
                commentCount
                user {
                    id
                    username
                }
            }
            ... on ResourceObjectType {
                id
                title
                score
                date
                starCount
                commentCount
                downloads
                resourceType {
                    name
                }
                user {
                    id
                    username
                }
            }
            ... on CommentObjectType {
                id
                text
                attachment
                created
                score
                user {
                    id
                    username
                    avatarThumbnail
                }
                replyComments {
                    id
                }
            }
        }
    """

    def query_suggestions(
        self,
        assert_error: bool = False,
    ) -> JsonDict:
        # language=GraphQL
        graphql = (
            self.suggestion_fields
            + """
                query Suggestions {
                    suggestions {
                        ...suggestionFields
                    }
                }
            """
        )

        return self.execute(graphql, assert_error=assert_error)

    def query_suggestions_preview(
        self,
        assert_error: bool = False,
    ) -> JsonDict:
        # language=GraphQL
        graphql = (
            self.suggestion_fields
            + """
                query SuggestionsPreview {
                    suggestionsPreview {
                        ...suggestionFields
                    }
                }
            """
        )

        return self.execute(graphql, assert_error=assert_error)

    # TODO: Update the `assert_field_fragment_matches_schema` test to support unions.
    def test_field_fragment(self) -> None:
        pass

    def test_suggestestions(self) -> None:
        self.authenticated_user = None

        # Test full suggestions.
        res = self.query_suggestions()
        assert len(res) == settings.SUGGESTIONS_COUNT

        courses = 0
        resources = 0
        comments = 0

        for result in res:
            if "name" in result:
                courses += 1

            if "title" in result:
                resources += 1

            if "text" in result:
                comments += 1

        assert courses == resources == comments == settings.SUGGESTIONS_COUNT / 3

        # Test suggestions preview.
        res = self.query_suggestions_preview()
        assert len(res) <= settings.SUGGESTIONS_PREVIEW_COUNT

        courses = 0
        resources = 0
        comments = 0

        for result in res:
            if "name" in result:
                courses += 1

            if "title" in result:
                resources += 1

            if "text" in result:
                comments += 1

        assert (
            courses == resources == comments == settings.SUGGESTIONS_PREVIEW_COUNT / 3
        )

        # TODO: Test remaining cases for the suggestions algorithm.
