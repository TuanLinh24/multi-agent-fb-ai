"""
Chat qua terminal — gọi API FastAPI /chat (SSE), không cần frontend.

Chạy server trước (ví dụ): uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Sau đó: python scripts/terminal_chat.py
"""
import json
import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx is not installed. Please install it with 'pip install httpx'.")
    sys.exit(1)

API_URL = os.environ.get("CHAT_API_URL", "http://127.0.0.1:8000/chat")
SESSION_ID = os.environ.get("CHAT_SESSION_ID", "terminal-session")
TIMEOUT = float(os.environ.get("CHAT_TIMEOUT", "120"))


def _streaming_response_error_detail(response: httpx.Response) -> str:
    """Với response từ client.stream(), phải read() trước khi dùng .text."""
    try:
        response.read()
    except Exception:
        pass
    try:
        return (response.text or "").strip()
    except httpx.ResponseNotRead:
        return ""


def _parse_sse_line(line: str) -> tuple[str | None, str | None]:
    if line.startswith("event:"):
        return ("event", line[6:].strip())
    if line.startswith("data:"):
        return ("data", line[5:].strip())
    return (None, None)


def stream_chat(message: str) -> None:
    payload = {"session_id": SESSION_ID, "message": message}
    parts: list[str] = []
    current_event: str | None = None

    with httpx.Client(timeout=TIMEOUT) as client:
        with client.stream("POST", API_URL, json=payload) as resp:
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = _streaming_response_error_detail(exc.response)
                suffix = detail if detail else "(không có nội dung phản hồi)"
                print(f"\nAPI lỗi {exc.response.status_code}: {suffix}")
                return

            for raw in resp.iter_lines():
                if raw is None:
                    continue
                line = raw.strip()
                if not line:
                    current_event = None
                    continue

                kind, value = _parse_sse_line(line)
                if kind == "event":
                    current_event = value
                elif kind == "data" and current_event == "token":
                    try:
                        obj = json.loads(value)
                    except json.JSONDecodeError:
                        continue
                    token = obj.get("token")
                    if token is not None:
                        parts.append(str(token))
                        print(str(token), end=" ", flush=True)
                elif kind == "data" and current_event == "complete":
                    print()
                    return

    # Nếu server không gửi event complete
    if parts:
        print()


def main() -> None:
    print("=== Multi-agent terminal chat (SSE) ===")
    print("API:", API_URL)
    print("Gõ 'exit', 'quit' hoặc Ctrl+C để thoát.\n")

    while True:
        try:
            message = input("Bạn: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nĐã thoát.")
            break

        if not message:
            continue
        if message.lower() in {"exit", "quit", "thoát"}:
            print("Đã thoát.")
            break

        try:
            print("Bot: ", end="", flush=True)
            stream_chat(message)
        except httpx.RequestError as exc:
            print(f"\nLỗi kết nối: {exc}")


if __name__ == "__main__":
    main()
