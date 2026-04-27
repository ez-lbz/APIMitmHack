from flask import Response
import json

try:
    from .config_loader import LOG_PATH
except ImportError:
    from config_loader import LOG_PATH


def append_log(section_text):
    try:
        with LOG_PATH.open("a", encoding="utf-8") as file:
            boundary = "=" * 60
            file.write(f"\n{boundary}\n{section_text}\n{boundary}\n")
    except Exception as ex:
        print(f"[!] Write log error: {ex}")


def parse_json(body_bytes):
    try:
        return json.loads(body_bytes.decode("utf-8", errors="replace"))
    except Exception:
        return {}


def extract_text_content(content):
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "".join(parts)

    return ""


def get_last_user_content(payload):
    for message in reversed(payload.get("messages", [])):
        if isinstance(message, dict) and message.get("role") == "user":
            return extract_text_content(message.get("content", ""))
    return ""


def get_model_name(payload, default_value):
    model_name = payload.get("model")
    if isinstance(model_name, str) and model_name.strip():
        return model_name
    return default_value


def prettify_text_if_json(text):
    try:
        return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    except Exception:
        return text


def redact_headers(headers, secret_headers):
    lines = []
    for key, value in headers:
        if key.lower() in secret_headers:
            lines.append(f"{key}: ***REDACTED***")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def build_response_headers(resp):
    excluded_headers = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    return [
        (name, value)
        for name, value in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]


def stream_proxy_response(resp, request_log, response_headers):
    def generate():
        response_content = b""
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                response_content += chunk
                yield chunk

        decoded_content = response_content.decode("utf-8", errors="replace")
        response_log = f"HTTP/1.1 {resp.status_code} {resp.reason}\n"
        for key, value in response_headers:
            response_log += f"{key}: {value}\n"
        response_log += f"\n{prettify_text_if_json(decoded_content)}"
        append_log(f"[Request]\n{request_log}\n\n[Response]\n{response_log}")

    return Response(generate(), status=resp.status_code, headers=response_headers)


def chunk_json_chars(data):
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ": "))
    return list(encoded)
