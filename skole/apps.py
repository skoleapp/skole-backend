import logging
from functools import wraps
from traceback import format_exception
from types import TracebackType
from typing import Optional

from django.apps import AppConfig
from graphql.execution.utils import ExecutionContext
from graphql_jwt.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


class SkoleAppConfig(AppConfig):
    name = "skole"

    def ready(self) -> None:
        import skole.signals  # noqa


@wraps(ExecutionContext.report_error)
def _patched_report_error(
    self: ExecutionContext, error: Exception, traceback: Optional[TracebackType] = None,
) -> None:
    exception = format_exception(
        type(error), error, getattr(error, "stack", None) or traceback
    )
    if not type(getattr(error, "original_error", None)) == PermissionDenied:
        logger.error("".join(exception))
    self.errors.append(error)


# Monkey patch this to have full control over what exceptions are logged.
setattr(ExecutionContext, "report_error", _patched_report_error)
