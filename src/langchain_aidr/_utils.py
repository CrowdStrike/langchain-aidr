from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


def guarded_content(guard_output: Mapping[str, object] | None, default: str) -> str:
    """
    Extract the content of the last message in an AI Guard `guard_output`,
    falling back to `default` if it is absent or malformed.
    """

    if not guard_output:
        return default

    messages = guard_output.get("messages")
    if not isinstance(messages, list) or not messages:
        return default

    last = messages[-1]
    if not isinstance(last, dict):
        return default

    content = last.get("content")
    return content if isinstance(content, str) else default
