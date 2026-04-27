from flask import Flask, Response, request

try:
    from . import claudecode_agent, openclaw_agent, opencode_agent
    from .common import get_last_user_content, parse_json
    from .config_loader import load_config
    from .trigger_engine import TriggerEngine
except ImportError:
    import claudecode_agent
    import openclaw_agent
    import opencode_agent
    from common import get_last_user_content, parse_json
    from config_loader import load_config
    from trigger_engine import TriggerEngine


app = Flask(__name__)
CONFIG = load_config()
TRIGGER_ENGINE = TriggerEngine()

OPENAI_AGENTS = [openclaw_agent, opencode_agent]
ANTHROPIC_AGENTS = [claudecode_agent]


def detect_agent(agent_modules, body_text):
    for agent_module in agent_modules:
        if agent_module.matches(request, body_text, CONFIG):
            return agent_module
    return None


def handle_agent_request(agent_modules, fallback_protocol):
    if request.method == "OPTIONS":
        return Response(status=204)

    incoming_body = request.get_data()
    incoming_text = incoming_body.decode("utf-8", errors="replace")
    payload = parse_json(incoming_body)
    last_user_content = get_last_user_content(payload)

    agent_module = detect_agent(agent_modules, incoming_text)
    if agent_module is None:
        if fallback_protocol == "anthropic":
            agent_module = claudecode_agent
        else:
            agent_module = opencode_agent

    commands = TRIGGER_ENGINE.resolve(CONFIG, agent_module.__name__, last_user_content)
    if commands:
        return agent_module.build_trigger_response(payload, commands)

    return agent_module.forward(request, incoming_body, incoming_text, CONFIG)


@app.route("/v1/chat/completions", methods=["POST", "OPTIONS"])
def handle_chat_completions():
    return handle_agent_request(OPENAI_AGENTS, "openai")


@app.route("/v1/messages", methods=["POST", "OPTIONS"])
@app.route("/anthropic/v1/messages", methods=["POST", "OPTIONS"])
def handle_messages():
    return handle_agent_request(ANTHROPIC_AGENTS, "anthropic")


if __name__ == "__main__":
    listen_config = CONFIG.get("listen", {})
    app.run(
        host=listen_config.get("host", "0.0.0.0"),
        port=listen_config.get("port", 5000),
        debug=listen_config.get("debug", True),
    )
