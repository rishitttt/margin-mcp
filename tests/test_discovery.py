from datetime import date

from margin_mcp.discovery import discovery_plan


def test_unknown_issuer_does_not_invent_a_company_website_or_identity():
    plan = discovery_plan("Unresolved Example", date(2025, 9, 30), "annual_report")
    assert not plan.issuer_identity_verified
    assert len(plan.sources) == 2
    assert all(source.status == "directory_lead_not_fetched" for source in plan.sources)
    assert "not that the company or filing does not exist" in plan.steps


def test_exact_alias_only_and_no_substring_identity_match():
    exact = discovery_plan(
        "Tata Consultancy Services Limited", date(2025, 9, 30), "financial_results"
    )
    ambiguous = discovery_plan("TCS or Infosys", date(2025, 9, 30), "financial_results")
    assert len(exact.sources) == 3
    assert len(ambiguous.sources) == 2
    assert not exact.issuer_identity_verified
