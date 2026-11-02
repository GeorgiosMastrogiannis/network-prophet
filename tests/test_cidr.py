import pytest

from network_guardian.cidr import cidrs_overlap


@pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="Exercise 1 is awaiting your implementation")
@pytest.mark.parametrize("left,right,expected", [
    ("10.0.0.0/24", "10.0.0.0/24", True),
    ("10.0.0.0/16", "10.0.2.0/24", True),
    ("10.0.0.0/24", "10.0.1.0/24", False),
    ("2001:db8::/32", "2001:db8:1::/48", True),
    ("0.0.0.0/0", "::/0", False),
])
def test_overlap(left, right, expected):
    assert cidrs_overlap(left, right) is expected
    assert cidrs_overlap(right, left) is expected


@pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="Exercise 1 is awaiting your implementation")
@pytest.mark.parametrize("invalid", ["bad", "10.0.0.1/24", "10.0.0.0/99"])
def test_invalid_cidr(invalid):
    with pytest.raises(ValueError):
        cidrs_overlap(invalid, "10.0.0.0/24")
