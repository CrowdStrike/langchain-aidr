from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from langchain_core.documents import Document
from pydantic import SecretStr

from langchain_aidr import CrowdStrikeGuardTransformer


def _transformer(reply: object) -> CrowdStrikeGuardTransformer:
    transformer = CrowdStrikeGuardTransformer(
        token=SecretStr("my_api_token"),
        base_url_template="https://api.crowdstrike.com/aidr/{SERVICE_NAME}",
    )
    transformer._client = MagicMock()
    transformer._client.guard_chat_completions.return_value = reply
    return transformer


def test_error_for_missing_result_does_not_contain_the_document() -> None:
    transformer = _transformer(SimpleNamespace(result=None))
    document = Document(page_content="private document text", metadata={"owner": "alice"})

    with pytest.raises(AssertionError) as excinfo:
        transformer.transform_documents([document])

    assert "private document text" not in str(excinfo.value)
    assert "alice" not in str(excinfo.value)


def test_guarded_content_replaces_page_content() -> None:
    guard_output = {"messages": [{"role": "user", "content": "redacted text"}]}
    transformer = _transformer(SimpleNamespace(result=SimpleNamespace(guard_output=guard_output)))

    documents = transformer.transform_documents([Document(page_content="original text", metadata={"k": "v"})])

    assert documents[0].page_content == "redacted text"
    assert documents[0].metadata == {"k": "v"}
