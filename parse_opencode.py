#!/usr/bin/env python3
import json
import sys


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_tools(data):
    results = []

    if isinstance(data, dict):
        if isinstance(data.get("tools"), list):
            results.extend(data["tools"])

        for value in data.values():
            results.extend(extract_tools(value))

    elif isinstance(data, list):
        for item in data:
            results.extend(extract_tools(item))

    return results


def get_tool_info(tool):
    if not isinstance(tool, dict):
        return None, None

    if tool.get("type") == "function":
        fn = tool.get("function", {})
        return fn.get("name"), fn.get("description", "")

    return tool.get("name") or tool.get("type"), tool.get("description", "")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} input.json", file=sys.stderr)
        sys.exit(1)

    data = load_json(sys.argv[1])
    tools = extract_tools(data)

    seen = set()

    for tool in tools:
        name, description = get_tool_info(tool)
        if not name or name in seen:
            continue

        seen.add(name)
        description = " ".join((description or "").split())

        print(f"{name}   {description}")


if __name__ == "__main__":
    main()