import json
import subprocess
import sys
from pathlib import Path

from ai_agent_service.harness.skill_graph import run_harness_skill


def test_langgraph_harness_skill_calls_jimmy_visit_tool(tmp_path: Path):
    source = tmp_path / "source.txt"
    output = tmp_path / "visited.txt"
    source.write_text("這是我的 skill 測試文件。\n", encoding="utf-8")

    result = run_harness_skill(
        skill_path="examples/skills/jimmy-visit-skill/SKILL.md",
        arguments={"input_path": str(source), "output_path": str(output)},
    )

    assert result["status"] == "verified"
    assert result["skill"]["name"] == "jimmy-visit-skill"
    assert result["selected_tool"] == "jimmy_visit_document"
    assert result["tool_result"]["ok"] is True
    assert "initialize" in result["steps"]
    assert "verify" in result["steps"]
    assert output.read_text(encoding="utf-8") == "這是我的 skill 測試文件。\n\nJimmy 到此一遊\n"


def test_langgraph_harness_skill_cli_outputs_json(tmp_path: Path):
    source = tmp_path / "source.txt"
    output = tmp_path / "visited.txt"
    source.write_text("CLI 測試。\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "examples/langgraph_skill_runner.py",
            "--skill",
            "examples/skills/jimmy-visit-skill/SKILL.md",
            "--input",
            str(source),
            "--output",
            str(output),
            "--json",
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["status"] == "verified"
    assert payload["selected_tool"] == "jimmy_visit_document"
    assert payload["verification"]["marker_present"] is True
    assert output.read_text(encoding="utf-8") == "CLI 測試。\n\nJimmy 到此一遊\n"
