import pytest


@pytest.mark.xfail
def test_should_fail():
    assert 1 == "I want this test to to fail"
