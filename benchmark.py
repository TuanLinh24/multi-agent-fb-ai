import time
import requests


url = "http://127.0.0.1:8000/chat"

payload = {
    "session_id": "1",
    "message": "Password wifi quán?"
}

start = time.time()

response = requests.post(
    url,
    json=payload
)

end = time.time()

print(response.text)

print(f"Latency: {end - start:.2f}s")