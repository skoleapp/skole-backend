import logging
from functools import update_wrapper
from traceback import format_exception
from types import TracebackType
from typing import Any, Optional

import graphql.execution.utils
from graphql_jwt.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


def patch(obj: Any, value: Any) -> None:
    setattr(obj, value.__name__, update_wrapper(value, getattr(obj, value.__name__)))


def report_error(
    self: graphql.execution.utils.ExecutionContext,
    error: Exception,
    traceback: Optional[TracebackType] = None,
) -> None:
    exception = format_exception(
        type(error), error, getattr(error, "stack", None) or traceback
    )
    if not type(getattr(error, "original_error", None)) == PermissionDenied:
        logger.error("".join(exception))
    self.errors.append(error)


patch(graphql.execution.utils.ExecutionContext, report_error)
