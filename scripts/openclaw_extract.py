#!/usr/bin/env python3
# extract_system_prompt.py

import json
import sys
from pathlib import Path


def extract_system_prompt(path: str) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    text = file_path.read_text(encoding="utf-8")

    data = json.loads(text)

    messages = data.get("messages", [])
    if not isinstance(messages, list):
        raise ValueError("JSON 中没有有效的 messages 列表")

    for msg in messages:
        if msg.get("role") == "system":
            content = msg.get("content", "")
            if not content:
                raise ValueError("找到了 system 消息，但 content 为空")
            return content

    raise ValueError("没有找到 role 为 system 的消息")


def main():
    if len(sys.argv) < 2:
        print("用法: python extract_system_prompt.py <json文件路径>")
        sys.exit(1)

    input_path = sys.argv[1]

    try:
        system_prompt = extract_system_prompt(input_path)

        output_path = Path("system_prompt.txt")
        output_path.write_text(system_prompt, encoding="utf-8")

        print("已提取 system prompt")
        print(f"输出文件: {output_path.resolve()}")
        print()
        print("预览前 1000 字:")
        print("-" * 60)
        print(system_prompt[:1000])

    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()