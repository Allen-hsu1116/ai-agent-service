#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from typing import Any

from ai_agent_service.harness.skill_graph import run_harness_skill


def parse_key_value(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"--arg must use KEY=VALUE format, got: {value}")
        key, raw = value.split("=", 1)
        parsed[key] = raw
    return parsed


def build_arguments(args: argparse.Namespace) -> dict[str, Any]:
    arguments = parse_key_value(args.arg)
    if args.input:
        arguments["input_path"] = args.input
    if args.output:
        arguments["output_path"] = args.output
    return arguments


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a SKILL.md through a small LangGraph + Harness workflow."
    )
    parser.add_argument("--skill", required=True, help="Path to a SKILL.md file with a tool key.")
    parser.add_argument("--input", help="Convenience alias for --arg input_path=...")
    parser.add_argument("--output", help="Convenience alias for --arg output_path=...")
    parser.add_argument(
        "--arg",
        action="append",
        default=[],
        help="Additional skill argument in KEY=VALUE format. Can be repeated.",
    )
    parser.add_argument("--json", action="store_true", help="Print the full final graph state as JSON.")
    args = parser.parse_args()

    result = run_harness_skill(skill_path=args.skill, arguments=build_arguments(args))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"status: {result['status']}")
    print(f"skill: {result['skill']['name']}")
    print(f"tool: {result['selected_tool']}")
    print(f"steps: {' -> '.join(result['steps'])}")
    print(f"verification: {json.dumps(result['verification'], ensure_ascii=False)}")


if __name__ == "__main__":
    main()
