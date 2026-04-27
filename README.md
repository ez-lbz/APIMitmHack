# MitmHack

用于搭建恶意的中转站，实现钓鱼攻击。当中转被用于 `opencode`，`claudecode`，`openclaw` 时可以实现直接通过劫持 response 来 tool call，从而执行系统命令。考虑到一般没有人在 `codex` 和 `antigravity` 中使用第三方 API，因此暂时不做支持。

当前项目只是一个简单的 demo，有 hw 需求的师傅可以自行二开，增强对不同 agent 的兼容性，以及将命令执行替换为上线免杀 c2。

## 项目结构

- `src/`: 主程序与路由逻辑，入口为 `src/app.py`
- `scripts/`: 独立实验脚本，用于代理转发、日志记录和触发式响应测试

## scripts 说明

- `scripts/mitm_openai.py`: OpenAI 兼容接口代理，转发请求并记录请求/响应日志
- `scripts/mitm_anthropic.py`: Anthropic 兼容接口代理，支持 `/v1/messages` 路由转发与日志记录
- `scripts/opencode_mitm_calc.py`: OpenAI 风格的触发脚本，命中特定关键词后返回伪造 `bash` 工具调用
- `scripts/openclaw_mitm_calc.py`: OpenAI 风格的流式触发脚本，返回分片的伪造工具调用响应
- `scripts/claudecode_mitm_calc.py`: Anthropic 风格的触发脚本，返回伪造 `Bash` tool_use 事件流
- `scripts/openclaw_extract.py`: 从请求 JSON 中提取 `system` 消息内容并输出到 `system_prompt.txt`
