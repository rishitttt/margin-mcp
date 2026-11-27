import io
import json

import pytest

from margin.evidence.sanitize import Sanitizer
from margin.interfaces.agent.cli import main
from margin.interfaces.agent.client import BridgeError


@pytest.mark.parametrize("why", ["", " ", "line\nbreak", "x" * 281])
def test_invalid_why_stops_before_client_creation(why):
    def factory(*args, **kwargs):
        raise AssertionError("No client allowed for an invalid summary")

    output = io.StringIO()
    assert main(["--why", why, "status"], client_factory=factory, output=output) == 2
    assert json.loads(output.getvalue())["error"]["code"] == "invalid_summary"


def test_why_is_redacted_recorded_before_dispatch_and_remains_json(capsys):
    sequence = []
    secret = "fictional-private-key-123456789"
    sanitizer = Sanitizer([secret])

    def decision(command, why):
        sequence.append("decision")
        assert secret not in why
        return {"event_id": "fictional-event"}

    def factory(*args, **kwargs):
        sequence.append("client")
        raise BridgeError("unavailable", "Fictional offline test")

    output = io.StringIO()
    assert (
        main(
            ["--why", "Inspect " + secret, "status"],
            client_factory=factory,
            decision_observer=decision,
            output_filter=sanitizer.clean,
            output=output,
        )
        == 2
    )
    value = json.loads(output.getvalue())
    assert sequence == ["decision", "client"]
    assert value["decision_event_id"] == "fictional-event"
    assert secret not in capsys.readouterr().err + output.getvalue()


def test_preexecution_log_failure_stops_client():
    def decision(*args):
        raise OSError("Fictional full disk")

    def factory(*args, **kwargs):
        raise AssertionError("No dispatch after recording failure")

    output = io.StringIO()
    assert (
        main(
            ["--why", "Inspect readiness.", "status"],
            client_factory=factory,
            decision_observer=decision,
            output=output,
        )
        == 2
    )
    assert json.loads(output.getvalue())["error"]["code"] == "recording"
