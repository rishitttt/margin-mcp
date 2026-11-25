"""Offline guard checks for the explicitly opted-in, bounded live diagnostic."""

import runpy
from pathlib import Path

import pytest

from margin.core.contracts import DomainError

CHECKER = runpy.run_path(str(Path(__file__).parents[1] / "scripts/check_drishti_review.py"))


@pytest.mark.parametrize("balance", ["NaN", "Infinity", None, 7, -1])
def test_account_preflight_never_authorizes_unknown_nonfinite_or_insufficient_balance(balance):
    with pytest.raises(DomainError):
        CHECKER["assert_access"]({"balance": balance, "status": "active"})


def test_detail_selector_never_follows_another_company_or_invents_a_missing_selector():
    def result(row):
        return {"payload_kind": "rest_json", "payload": {"data": [row]}}

    assert CHECKER["detail_request"](result({"symbol": "OTHER", "id": "real-but-wrong"})) is None
    assert CHECKER["detail_request"](result({"symbol": "INFY"})) is None
    assert CHECKER["detail_request"](result({"symbol": "INFY", "id": "returned-id"})) == {
        "operation": "drishti.get_earnings_filing",
        "arguments": {"earnings_id": "returned-id", "detailed": True},
    }
