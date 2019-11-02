from pytest import fixture


def test_str(subject: fixture) -> None:
    assert str(subject) == "Test subject"
