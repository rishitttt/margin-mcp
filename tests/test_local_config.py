import pytest

from margin.interfaces.agent.client import BridgeError
from margin.interfaces.agent.local_config import read_provider_env


def test_credential_file_is_data_and_only_loads_provider_names(tmp_path):
    path = tmp_path / "providers.env"
    path.write_text(
        "# local test\nexport BHARATSTOCK_API_KEY='literal-$(not-a-command)'\nDRISHTI_API_KEY=fictional-drishti-test\nOTHER_SECRET=ignored\n"
    )
    values = read_provider_env(path)
    assert values == {
        "BHARATSTOCK_API_KEY": "literal-$(not-a-command)",
        "DRISHTI_API_KEY": "fictional-drishti-test",
    }
    path.write_text("BHARATSTOCK_API_KEY='broken-quote\n")
    with pytest.raises(BridgeError, match="valid local provider"):
        read_provider_env(path)
