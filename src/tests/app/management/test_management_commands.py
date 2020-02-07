from typing import Any
from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError


class CommandTests:
    def test_wait_for_db_ready(self) -> None:
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.return_value = True
            call_command("wait_for_db")
            assert gi.call_count == 1

    @patch("time.sleep", return_value=True)
    def test_wait_for_db(self, ts: Any) -> None:
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.side_effect = [OperationalError] * 5 + [True]  # type: ignore
            call_command("wait_for_db")
            assert gi.call_count == 6
