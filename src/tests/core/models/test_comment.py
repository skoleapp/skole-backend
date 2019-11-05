from pytest import fixture


def test_str(comment: fixture) -> None:
    comment.text = "Please help me with this"
    assert str(comment) == "testuser: Please help me with ..."

    comment.text = "Please help me"
    assert str(comment) == "testuser: Please help me"
