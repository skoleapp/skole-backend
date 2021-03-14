import json
import re
import zipfile
from pathlib import Path

import magic
from django.conf import settings
from django.core import mail

from skole.tests.helpers import SkoleSchemaTestCase, get_form_error, get_graphql_error
from skole.types import ID, JsonDict
from skole.utils.constants import Messages


class GdprSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    def mutate_my_data(self, assert_error: bool = False) -> JsonDict:
        return self.execute_non_input_mutation(
            name="myData",
            result="successMessage",
            assert_error=assert_error,
        )

    def test_my_data(self) -> None:
        self.authenticated_user = 2
        assert len(mail.outbox) == 0

        res = self.mutate_my_data()
        assert not res["errors"]
        assert res["successMessage"] == Messages.DATA_REQUEST_RECEIVED

        assert len(mail.outbox) == 1
        sent = mail.outbox[0]

        # The mutation has a rate limit.
        res = self.mutate_my_data()
        assert res["successMessage"] is None
        assert "next time in" in get_form_error(res)
        assert len(mail.outbox) == 1

        assert "Your data request" in sent.subject
        assert sent.from_email == settings.EMAIL_ADDRESS
        assert sent.to == ["testuser2@test.com"]

        match = re.search(
            r"generated/my_data/(testuser2_data_\d{8})\w*\.zip", sent.body
        )
        assert match
        filepath = match.group(0)
        directory = match.group(1)

        data = f"{directory}/data.json"
        png = f"{directory}/uploads/attachments/test_attachment.png"
        jpg = f"{directory}/uploads/avatars/test_avatar.jpg"
        pdf = f"{directory}/uploads/resources/test_resource.pdf"

        with zipfile.ZipFile(Path(settings.MEDIA_ROOT) / filepath) as f:
            namelist = f.namelist()
            assert len(namelist) == 4
            assert data in namelist  # The order is not stable, so check individually.
            assert png in namelist
            assert jpg in namelist
            assert pdf in namelist
            assert "PNG" in magic.from_buffer(f.read(png))
            assert "JPEG" in magic.from_buffer(f.read(jpg))
            assert "PDF" in magic.from_buffer(f.read(pdf))
            content = json.loads(f.read(data))

        assert content["username"] == "testuser2"
        assert content["verified"] is True
        assert content["badges"] == ["Staff"]
        assert content["votes"] == [{"id": 1, "target": "comment 1", "vote": "upvote"}]
        assert content["stars"] == ["course 1", "course 2", "resource 1", "resource 2"]

    def test_my_data_login_required(self) -> None:
        self.authenticated_user = None
        res = self.mutate_my_data(assert_error=True)
        assert "permission" in get_graphql_error(res)
        assert res["data"] == {"myData": None}
        assert len(mail.outbox) == 0
