"""Deterministic workflow hints, without semantic judgments or transport imports."""

from copy import deepcopy


def step(function, bindings, required_host_fields=(), **context):
    return {
        "function": function,
        "bound_arguments": deepcopy(bindings),
        "required_host_fields": list(required_host_fields),
        "is_complete_input": not required_host_fields,
        "schema_source": "Exact review capability schema for this function; complete required host fields before calling.",
        **deepcopy(context),
    }


def packet_step(packet, function, required_host_fields=()):
    return step(
        function,
        {key: packet[key] for key in ("packet_id", "packet_hash")},
        required_host_fields,
        allowed_source_ids=[source["source_id"] for source in packet["sources"]],
        allowed_claim_ids=[claim["claim_id"] for claim in packet.get("claims", [])],
    )
