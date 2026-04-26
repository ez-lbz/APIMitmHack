from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

TARGET_URL = "https://api.deepseek.com/chat/completions"

@app.route('/v1/chat/completions', methods=['POST', 'OPTIONS'])
def proxy():
    if request.method == 'OPTIONS':
        return Response(status=204)

    client_auth = request.headers.get('Authorization')
    if not client_auth:
        return Response("Missing Authorization Header", status=401)

    proxy_headers = {
        "Content-Type": request.headers.get('Content-Type', 'application/json'),
        "Authorization": client_auth
    }

    incoming_body = request.get_data()

    print(f"[*] 收到请求，正在转发到: {TARGET_URL}")
    
    try:
        req_protocol = request.environ.get('SERVER_PROTOCOL', 'HTTP/1.1')
        req_log_str = f"{request.method} {request.path} {req_protocol}\n"
        for k, v in request.headers:
            req_log_str += f"{k}: {v}\n"
        req_log_str += f"\n{incoming_body.decode('utf-8', errors='replace')}"

        resp = requests.post(
            url=TARGET_URL,
            data=incoming_body,
            headers=proxy_headers,
            stream=True
        )

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        def generate():
            response_content = b""
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    response_content += chunk
                    yield chunk
            
            decoded_content = response_content.decode('utf-8', errors='replace')
            final_log_content = decoded_content

            content_type = resp.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                try:
                    final_log_content = json.dumps(
                        json.loads(decoded_content),
                        ensure_ascii=False,
                        indent=2
                    )
                except json.JSONDecodeError:
                    pass

            resp_log_str = f"HTTP/1.1 {resp.status_code} {resp.reason}\n"
            for k, v in headers:
                resp_log_str += f"{k}: {v}\n"
            resp_log_str += f"\n{final_log_content}"

            try:
                with open("llm.log", "a", encoding="utf-8") as f:
                    boundary = "=" * 60
                    f.write(f"\n{boundary}\n[Request]\n{req_log_str}\n\n[Response]\n{resp_log_str}\n{boundary}\n")
            except Exception as ex:
                print(f"[!] Write log error: {ex}")

        return Response(generate(),
                        status=resp.status_code,
                        headers=headers)

    except Exception as e:
        return Response(f"Proxy Error: {str(e)}", status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
