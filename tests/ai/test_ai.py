import asyncio
import importlib
import json

import pytest

from app.ai import tools
from tests.conftest import TEST_SECRET

EMPTY = {"title": "", "description": "", "status": "new", "priority": "0", "due_at": "", "tags": ""}


def test_tools_cover_the_whole_task_life(app):
    with app.app_context():
        task = tools.create_task({**EMPTY, "title": "Appeler le comptable", "priority": "3", "due_at": "2030-05-02T10:00", "tags": "admin"})
        assert (task["priority"], task["status"]) == ("Haute", "scheduled")
        task = tools.update_task(task["id"], {"description": "Bilan annuel", "title": None})
        assert task["description"] == "Bilan annuel" and task["tags"] == ["admin"]
        tools.add_subtask(task["id"], "Préparer les pièces")
        detail = tools.add_comment(task["id"], "Rappeler lundi")
        assert detail["subtasks"] == "0/1" and detail["comment_items"][0]["body"] == "Rappeler lundi"
        assert tools.move_task(task["id"], "done")["column"] == "Terminées"
        assert [item["id"] for item in tools.list_tasks("done", "", "", "")] == [task["id"]]
        assert tools.delete_task(task["id"])["deleted"] == task["id"]
        assert tools.list_tasks("", "", "", "") == []


def test_tools_reuse_web_validation(app):
    with app.app_context():
        with pytest.raises(ValueError, match="Données invalides"):
            tools.create_task(EMPTY)
        with pytest.raises(ValueError, match="Tag invalide"):
            tools.create_task({**EMPTY, "title": "ok", "tags": "<script>"})
        with pytest.raises(ValueError, match="Aucune tâche"):
            tools.get_task("1 OR 1=1")
        task = tools.create_task({**EMPTY, "title": "ok"})
        with pytest.raises(ValueError, match="Colonne inconnue"):
            tools.move_task(task["id"], "archived")
        with pytest.raises(ValueError, match="Données invalides"):
            tools.add_comment(task["id"], "x" * 1001)


def test_mcp_server_exposes_tools(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", TEST_SECRET)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "mcp.db"))
    monkeypatch.delenv("MCP_READ_ONLY", raising=False)
    server_module = importlib.reload(importlib.import_module("app.ai.server"))

    async def scenario():
        names = {tool.name for tool in await server_module.server.list_tools()}
        result = await server_module.server.call_tool("create_task", {"title": "Depuis l'IA", "tags": "ia"})
        listed = await server_module.server.call_tool("list_tasks", {"tag": "ia"})
        return names, result, listed

    names, result, listed = asyncio.run(scenario())
    assert names == {"list_tasks", "get_task", "create_task", "update_task", "move_task", "add_subtask", "add_comment", "delete_task"}
    assert result.is_error is False
    assert "Depuis l'IA" in json.dumps(listed.model_dump(), ensure_ascii=False)


def test_mcp_server_can_be_read_only(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", TEST_SECRET)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "mcp.db"))
    monkeypatch.setenv("MCP_READ_ONLY", "1")
    server_module = importlib.reload(importlib.import_module("app.ai.server"))
    names = {tool.name for tool in asyncio.run(server_module.server.list_tools())}
    assert names == {"list_tasks", "get_task"}
