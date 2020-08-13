import pickle

from graphql.execution.utils import ExecutionContext


def test_report_error_base_code_has_not_changed() -> None:
    # Make sure that we immediately notice if the source code of the method
    # we are monkey patching has changed, so that we can ensure full compatibility.
    expected = (
        b"\x80\x04\x95=\x00\x00\x00\x00\x00\x00\x00\x8c\x17graphql.execution.utils"
        b"\x94\x8c\x1dExecutionContext.report_error\x94\x93\x94."
    )
    assert pickle.dumps(ExecutionContext.report_error) == expected
