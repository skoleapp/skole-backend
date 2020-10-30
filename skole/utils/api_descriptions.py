from skole.models import (
    Activity,
    Badge,
    City,
    Comment,
    Country,
    Course,
    Resource,
    ResourceType,
    School,
    SchoolType,
    Star,
    Subject,
    User,
    Vote,
)


class APIDescriptions:
    """
    Used in object type, query and mutation descriptions that are injected to API docs.

    Descriptions must be single-line to have a decent formatting on the GraphiQL.
    Descriptions are also not translated as they are only used for improved developer
    experience and proper API documentation.
    """

    # Information used by multiple queries and mutations.

    AUTH_REQUIRED = "Only allowed for authenticated users."
    PAGINATED = "Results are paginated."
    CREATION_TIME_SORTING = "Results are sorted by creation time."
    MUTATION_ERROR_DESCRIPTION = "Return an error if in the following cases:"
    USER_NOT_FOUND = "A user account with the provided email address was not found."
    EMAIL_ERROR = "An unknown error while sending the email occurred."
    AUTOCOMPLETE_QUERY = "Return limited amount of results for autocomplete fields."
    ALPHABETIC_SORTING = "Results are sorted alphabetically."
    DETAIL_QUERY = "Return a single object based on the ID. If an object is not found or it has been soft deleted, return `null` instead."
    VERIFIED_OWNERSHIP_REQUIRED = "Only allowed for authenticated users that have verified their accounts and are the creators of the object."
    NUM_COURSES_SORTING = "Results are sorted by amount of courses."

    VERIFICATION_REQUIRED = (
        "Only allowed for authenticated users that have verified their accounts."
    )

    OWNERSHIP_REQUIRED = (
        "Only allowed for authenticated users that are the creators of the object."
    )

    # Object types. Descriptions are either directly model class docstrings or they are extended from those.

    USER_OBJECT_TYPE = f"{User.__doc__} The following fields are private, meaning they are returned only if the user is querying one's own profile: `email`, `verified`, `school`, `subject`. For instances that are not the user's own user profile, these fields will return a `null` value."
    ACTIVITY_OBJECT_TYPE = Activity.__doc__
    PAGINATED_ACTIVITY_OBJECT_TYPE = f"{ACTIVITY_OBJECT_TYPE} {PAGINATED}"
    BADGE_OBJECT_TYPE = Badge.__doc__
    CITY_OBJECT_TYPE = City.__doc__
    COMMENT_OBJECT_TYPE = Comment.__doc__
    COUNTRY_OBJECT_TYPE = Country.__doc__
    COURSE_OBJECT_TYPE = Course.__doc__
    PAGINATED_COURSE_OBJECT_TYPE = f"{COURSE_OBJECT_TYPE} {PAGINATED}"
    RESOURCE_TYPE_OBJECT_TYPE = ResourceType.__doc__
    RESOURCE_OBJECT_TYPE = Resource.__doc__
    PAGINATED_RESOURCE_OBJECT_TYPE = f"{RESOURCE_OBJECT_TYPE} {PAGINATED}"
    SCHOOL_TYPE_OBJECT_TYPE = SchoolType.__doc__
    SCHOOL_OBJECT_TYPE = School.__doc__
    STAR_OBJECT_TYPE = Star.__doc__
    SUBJECT_OBJECT_TYPE = Subject.__doc__
    PAGINATED_SUBJECT_OBJECT_TYPE = f"{SUBJECT_OBJECT_TYPE} {PAGINATED}"
    VOTE_OBJECT_TYPE = Vote.__doc__

    # User queries.

    USER_ME = f"Return user profile of the user making the query. {AUTH_REQUIRED}"
    USER = f"{DETAIL_QUERY} Superusers cannot be queried."
    CREATED_COURSES = f"Return courses created by the user provided as a parameter. {PAGINATED} {CREATION_TIME_SORTING}"
    CREATED_RESOURCES = f"Return resources created by the user provided as a parameter. {PAGINATED} {CREATION_TIME_SORTING}"
    STARRED_COURSES = f"Return starred courses of the user making the query. {PAGINATED} {CREATION_TIME_SORTING} Return an empty list for unauthenticated users."
    STARRED_RESOURCES = f"Return starred resources of the user making the query. {PAGINATED} {CREATION_TIME_SORTING} Return an empty list for unauthenticated users."

    # User mutations.

    REGISTER_USER = "Register a new user. Check if there is an existing user with that email or username. Check that account is not deactivated. By default, set the user's account as unverified. After successful registration, send account verification email."
    VERIFY_ACCOUNT = "Receive the token that was sent by email. If the token is valid, verify the user's account."
    RESEND_VERIFICATION_EMAIL = f"Send verification email again.\n{MUTATION_ERROR_DESCRIPTION}\n- {USER_NOT_FOUND}\n- {EMAIL_ERROR}\n- The user has already verified one's account."
    SEND_PASSWORD_RESET_EMAIL = f"Send password reset email. For non-verified users, send a verification email instead and return an according error message.\n{MUTATION_ERROR_DESCRIPTION}\n- {USER_NOT_FOUND}\n- {EMAIL_ERROR}"
    RESET_PASSWORD = "Change user's password without knowing the old password. Receive the token that was sent by email. Revoke refresh token and require the user to log in again with one's new password."
    LOGIN = "Obtain JSON web token and user information. Non-verified users can still login."
    LOGOUT = f"Delete JSON web token cookie and logout. {AUTH_REQUIRED}"
    CHANGE_PASSWORD = f"Change password with a requirement of knowing the old password. {VERIFICATION_REQUIRED}"
    UPDATE_USER = f"Update some user model fields. {AUTH_REQUIRED}"

    DELETE_USER = (
        f"Soft delete account. The user must confirm his password. {AUTH_REQUIRED}"
    )

    # Activity queries.
    ACTIVITY = f"Return all activity of to the user making the query. {PAGINATED} {CREATION_TIME_SORTING} {AUTH_REQUIRED}"
    ACTIVITY_PREVIEW = (
        "Return limited amount of activity of the user making the query for a preview."
    )

    # Activity mutations.

    MARK_ACTIVITY_AS_READ = f"Mark a single activity read/unread. {AUTH_REQUIRED}"

    MARK_ALL_ACTIVITIES_AS_READ = (
        f"Mark all activities of the given user as read. {AUTH_REQUIRED}"
    )

    # City queries.

    AUTOCOMPLETE_CITIES = f"{AUTOCOMPLETE_QUERY} {ALPHABETIC_SORTING}"

    # Comment mutations.

    CREATE_COMMENT = (
        "Create a new comment. Attachments are popped of for unauthenticated users."
    )

    UPDATE_COMMENT = f"Update an existing comment. {OWNERSHIP_REQUIRED}"
    DELETE_COMMENT = f"Delete a comment. {OWNERSHIP_REQUIRED}"

    # Contact mutations.

    CREATE_CONTACT_MESSAGE = "Submit a message via the contact form."

    # Course queries.

    COURSES = f"Return courses filtered by query params. Results are sorted either manually based on query params or by secret Skole AI-powered algorithms. {PAGINATED}"

    AUTOCOMPLETE_COURSES = (
        f"{AUTOCOMPLETE_QUERY} Results are sorted by secret Skole AI-powered algorithms."
    )

    # Course mutations.

    CREATE_COURSE = f"Create a new course. {VERIFICATION_REQUIRED}"
    DELETE_COURSE = f"Delete a course. {OWNERSHIP_REQUIRED}"

    # Resource type queries.

    RESOURCE_TYPES = (
        f"Return unlimited amount of resource types. {CREATION_TIME_SORTING}"
    )

    AUTOCOMPLETE_RESOURCE_TYPES = f"{AUTOCOMPLETE_QUERY} {ALPHABETIC_SORTING}"

    # Resource mutations.

    CREATE_RESOURCE = f"Create a new resource. {VERIFICATION_REQUIRED}"
    UPDATE_RESOURCE = f"Update a resource. {VERIFIED_OWNERSHIP_REQUIRED}"
    DELETE_RESOURCE = f"Delete a resource. {VERIFIED_OWNERSHIP_REQUIRED}"

    # Resources queries.

    RESOURCES = f"Return resources based on the course ID. If no course with the provided ID is found, return an empty list. {PAGINATED} {CREATION_TIME_SORTING}."

    RESOURCE = "Return a single resource based on the resource ID."

    # School type queries.

    AUTOCOMPLETE_SCHOOL_TYPES = f"{AUTOCOMPLETE_QUERY} {CREATION_TIME_SORTING}"

    # School queries.

    AUTOCOMPLETE_SCHOOLS = f"{AUTOCOMPLETE_QUERY} {CREATION_TIME_SORTING}"

    # Star mutations.

    STAR = f"Mark a course or a resource with a star or remove the star if it already exists. {VERIFICATION_REQUIRED}"

    # Subject queries.

    SUBJECTS = f"Filter results based on the school ID. {NUM_COURSES_SORTING}"
    AUTOCOMPLETE_SUBJECTS = f"{AUTOCOMPLETE_QUERY} {NUM_COURSES_SORTING}"

    # Vote mutations.

    VOTE = f"Upvote, downvote or remove a vote from a course, resource or a comment. {VERIFICATION_REQUIRED}"
