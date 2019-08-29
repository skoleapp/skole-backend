from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.db.utils import OperationalError


@pytest.mark.django_db
@pytest.mark.management
class CommandTests:
    def test_wait_for_db_ready(self):
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.return_value = True
            call_command("wait_for_db")
            assert gi.call_count == 1

    @patch("time.sleep", return_value=True)
    def test_wait_for_db(self, ts):
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command("wait_for_db")
            assert gi.call_count == 6
