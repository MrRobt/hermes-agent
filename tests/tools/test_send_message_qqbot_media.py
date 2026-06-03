"""QQBot media delivery tests for tools/send_message_tool.py."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from gateway.config import Platform
from tools.send_message_tool import _send_to_platform


def test_qqbot_sends_image_via_live_adapter_when_media_present(tmp_path, monkeypatch):
    image_path = tmp_path / "photo.png"
    image_path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)

    adapter = SimpleNamespace(
        send=AsyncMock(return_value=SimpleNamespace(success=True, message_id="text-1", error=None)),
        send_image_file=AsyncMock(return_value=SimpleNamespace(success=True, message_id="image-1", error=None)),
    )
    runner = SimpleNamespace(adapters={Platform.QQBOT: adapter})
    monkeypatch.setattr("gateway.run._gateway_runner_ref", lambda: runner)

    result = asyncio.run(
        _send_to_platform(
            Platform.QQBOT,
            SimpleNamespace(enabled=True, token="***", extra={}),
            "9AC72512D97BFF1E49F1918F6D346777",
            "图片测试",
            media_files=[(str(image_path), False)],
        )
    )

    assert result["success"] is True
    assert result["message_id"] == "image-1"
    adapter.send.assert_awaited_once()
    adapter.send_image_file.assert_awaited_once_with(
        chat_id="9AC72512D97BFF1E49F1918F6D346777",
        image_path=str(image_path),
        metadata=None,
    )


def test_qqbot_sends_media_only_image_via_live_adapter(tmp_path, monkeypatch):
    image_path = tmp_path / "photo.png"
    image_path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)

    adapter = SimpleNamespace(
        send=AsyncMock(),
        send_image_file=AsyncMock(return_value=SimpleNamespace(success=True, message_id="image-only", error=None)),
    )
    runner = SimpleNamespace(adapters={Platform.QQBOT: adapter})
    monkeypatch.setattr("gateway.run._gateway_runner_ref", lambda: runner)

    result = asyncio.run(
        _send_to_platform(
            Platform.QQBOT,
            SimpleNamespace(enabled=True, token="***", extra={}),
            "9AC72512D97BFF1E49F1918F6D346777",
            "",
            media_files=[(str(image_path), False)],
        )
    )

    assert result["success"] is True
    assert result["message_id"] == "image-only"
    adapter.send.assert_not_awaited()
    adapter.send_image_file.assert_awaited_once()
