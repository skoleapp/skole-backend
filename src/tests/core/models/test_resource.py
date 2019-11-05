from pytest import fixture


def test_str(resource: fixture) -> None:
    assert str(resource) == "'Test exam' by testuser"
