# Multi-Agent Coffee Shop Chat Demo

## 🎯 Tổng quan

Demo giao diện chat đơn giản để minh họa luồng hội thoại đa lượt (multi-turn conversation) với hệ thống multi-agent AI cho quán coffee Highlands.

## 🤖 Các Agents

Demo sử dụng 4 agents khác nhau:

1. **🎯 Router Agent**: Phân loại câu hỏi và chuyển đến agent phù hợp
2. **❓ FAQ Agent**: Trả lời câu hỏi thường gặp
3. **💬 Consultant Agent**: Tư vấn về menu, dịch vụ
4. **🛒 Order Agent**: Xử lý đặt hàng

## 🚀 Cách chạy Demo

### 1. Khởi động Backend Services

```bash
# Khởi động Neo4j, Redis, vLLM
docker-compose -f docker/docker-compose.yml up -d

# Setup Neo4j schema
PYTHONPATH=. python scripts/setup_neo4j_schema.py

# Ingest dữ liệu
PYTHONPATH=. python scripts/ingest_data.py

# Khởi động FastAPI server
PYTHONPATH=. python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Mở Chat Demo

Mở file `chat_demo.html` trong trình duyệt web:

```bash
# Trên Windows
start chat_demo.html

# Hoặc mở trực tiếp trong VS Code / trình duyệt
```

## 💬 Cách sử dụng Demo

### Demo Buttons
- **❓ Hỏi FAQ**: "Wifi là gì?"
- **☕ Hỏi menu**: "Các loại coffee của quán?"
- **🛒 Đặt hàng**: "Tôi muốn đặt 2 ly latte"
- **💺 Hỏi tiện ích**: "Quán có chỗ ngồi ngoài trời không?"

### Multi-turn Conversation Examples

1. **Luồng FAQ**:
   ```
   User: Wifi là gì?
   Router → FAQ Agent: Highands123

   User: Quán mở cửa lúc mấy giờ?
   Router → FAQ Agent: 7h sáng đến 10h tối
   ```

2. **Luồng Tư vấn + Đặt hàng**:
   ```
   User: Các loại coffee của quán?
   Router → Consultant Agent: Latte, Americano, Mocha...

   User: Tôi muốn đặt 2 ly latte
   Router → Order Agent: Xử lý đơn hàng...
   ```

3. **Luồng hỗn hợp**:
   ```
   User: Quán có chỗ ngồi ngoài trời không?
   Router → Consultant Agent: Có khu vực ngoài trời

   User: Wifi password là gì?
   Router → FAQ Agent: Highlands123
   ```

## 🎨 Tính năng UI

- **💬 Real-time Chat**: Giao diện chat hiện đại với animations
- **⚡ Streaming Response**: Hiển thị token-by-token theo thời gian thực
- **📊 Performance Metrics**: Theo dõi TTFT, throughput, token count
- **🎭 Agent Indicators**: Hiển thị agent nào đang xử lý
- **📱 Responsive Design**: Hoạt động tốt trên mobile và desktop

## 🔧 Technical Features

### Streaming SSE
```javascript
// Nhận streaming response từ FastAPI
async displayStreamingResponse(response) {
    // Parse SSE events
    // Update UI token-by-token
    // Track performance metrics
}
```

### Agent Routing Visualization
```javascript
// Hiển thị agent nào đang xử lý
addMessage(content, isUser, agentType) {
    // Add agent info badge
    // Show routing animation
}
```

### Performance Monitoring
- **TTFT (Time to First Token)**: ≤ 0.2s target
- **Token Throughput**: Tokens per second
- **Total Token Count**: Per response

## 📈 Demo Scenarios

### Scenario 1: Khám phá Menu
```
User: Quán có những loại coffee nào?
→ Router Agent phân tích → Consultant Agent
→ Trả lời: Latte, Americano, Mocha, Tea Peach, Freeze

User: Latte có giá bao nhiêu?
→ Router Agent → Consultant Agent
→ Trả lời: 49,000 VND
```

### Scenario 2: Đặt hàng
```
User: Tôi muốn đặt 2 ly latte và 1 mocha
→ Router Agent → Order Agent
→ Xử lý đơn hàng và xác nhận
```

### Scenario 3: Thông tin chung
```
User: Quán có wifi không?
→ Router Agent → FAQ Agent
→ Trả lời: Có, password: Highlands123

User: Mở cửa từ mấy giờ?
→ Router Agent → FAQ Agent
→ Trả lời: 7h sáng - 10h tối
```

## 🎯 Key Benefits

1. **Multi-turn Context**: Duy trì ngữ cảnh cuộc hội thoại
2. **Agent Specialization**: Mỗi agent chuyên về một lĩnh vực
3. **Seamless Routing**: Router tự động chuyển agent phù hợp
4. **Real-time Streaming**: Trải nghiệm chat mượt mà
5. **Performance Tracking**: Giám sát chất lượng hệ thống

## 🔍 Troubleshooting

### Backend không chạy
```bash
# Check services
docker ps

# Check FastAPI logs
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Chat không hoạt động
```bash
# Check CORS settings
# Verify API endpoint: http://localhost:8000/chat
# Check browser console for errors
```

### Performance issues
```bash
# Check vLLM service
docker logs vllm-container

# Monitor Neo4j
# Check Redis connection
```

## 📚 API Reference

### POST /chat
```json
{
  "session_id": "string",
  "message": "string"
}
```

**Response**: Server-Sent Events với streaming tokens

### GET /health
Trả về trạng thái các services

### GET /benchmark
Chạy benchmark performance test

---

## 🎉 Kết luận

Demo này minh họa thành công khả năng của hệ thống multi-agent trong việc xử lý các cuộc hội thoại phức tạp, với routing thông minh và streaming responses real-time. Đây là nền tảng vững chắc cho các ứng dụng AI conversation tiên tiến.