import json
from pathlib import Path

import pytest

from margin_mcp.models import Corpus
from margin_mcp.services import ResearchService
from margin_mcp.storage import CorpusStore

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def payload():
    return json.loads((ROOT / "examples/synthetic-corpus.json").read_text())


@pytest.fixture
def corpus(payload):
    return Corpus.model_validate(payload)


@pytest.fixture
def store(tmp_path, corpus):
    store = CorpusStore(tmp_path / "corpus.sqlite3")
    store.import_corpus(corpus)
    return store


@pytest.fixture
def service(store):
    return ResearchService(store)


@pytest.fixture
def anyio_backend():
    return "asyncio"
