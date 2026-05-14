import time
import requests
import json

url = "http://127.0.0.1:8000/chat"

payload = {
    "session_id": "benchmark",
    "message": "Món nào bán chạy nhất?"
}

def measure_ttft_and_total():
    start_time = time.time()

    response = requests.post(url, json=payload, stream=True)
    print(f"Status: {response.status_code}")

    first_token_time = None
    total_tokens = 0

    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            print(f"Line: {line}")
            if line.startswith('data: '):
                data = line[6:]
                if data == '[DONE]':
                    break
                try:
                    event = json.loads(data)
                    print(f"Event: {event}")
                    if 'token' in event:
                        if first_token_time is None:
                            first_token_time = time.time()
                        total_tokens += 1
                except json.JSONDecodeError as e:
                    print(f"JSON error: {e}")
                    pass

    end_time = time.time()

    ttft = (first_token_time - start_time) * 1000 if first_token_time else None  # ms
    total_latency = (end_time - start_time) * 1000  # ms

    print(f"TTFT: {ttft} ms")
    print(f"Total Latency: {total_latency:.2f} ms")
    print(f"Total Tokens: {total_tokens}")

    return ttft, total_latency

if __name__ == "__main__":
    measure_ttft_and_total()