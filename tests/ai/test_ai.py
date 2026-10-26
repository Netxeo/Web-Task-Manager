import asyncio
import importlib
import json

import pytest

from app.ai import tools
from tests.conftest import TEST_SECRET


def test_tools_create_update_complete_delete(app):
    with app.app_context():
        task = tools.create_task({"title": "Appeler le comptable", "description": "", "priority": "3", "due_at": "2030-05-02T10:00", "tags": "admin"})
        assert task["priority"] == "Haute"
        task = tools.update_task(task["id"], {"title": None, "description": "Bilan annuel", "priority": None, "due_at": None, "tags": None})
        assert task["description"] == "Bilan annuel"
        assert task["tags"] == ["admin"]
        assert tools.set_done(task["id"], True)["done"] is True
        assert tools.list_tasks("done", "", "", "", "recent")[0]["id"] == task["id"]
        assert tools.delete_task(task["id"])["deleted"] == task["id"]
        assert tools.list_tasks("todo", "", "", "", "recent") == []


def test_tools_reuse_web_validation(app):
    with app.app_context():
        with pytest.raises(ValueError, match="Données invalides"):
            tools.create_task({"title": "", "description": "", "priority": "0", "due_at": "", "tags": ""})
        with pytest.raises(ValueError, match="Tag invalide"):
            tools.create_task({"title": "ok", "description": "", "priority": "0", "due_at": "", "tags": "<script>"})
        with pytest.raises(ValueError, match="Aucune tâche"):
            tools.get_task("1 OR 1=1")


def test_mcp_server_exposes_tools(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", TEST_SECRET)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "mcp.db"))
    server_module = importlib.reload(importlib.import_module("app.ai.server"))

    async def scenario():
        names = {tool.name for tool in await server_module.server.list_tools()}
        result = await server_module.server.call_tool("create_task", {"title": "Depuis l'IA", "tags": "ia"})
        listed = await server_module.server.call_tool("list_tasks", {"tag": "ia"})
        return names, result, listed

    names, result, listed = asyncio.run(scenario())
    assert names == {"list_tasks", "get_task", "create_task", "update_task", "set_task_done", "delete_task"}
    assert result.is_error is False
    assert "Depuis l'IA" in json.dumps(listed.model_dump(), ensure_ascii=False)
