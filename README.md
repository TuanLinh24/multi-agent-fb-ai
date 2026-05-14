# Multi-Agent Coffee Shop AI System

## 🎯 Tổng quan

Hệ thống AI đa tác tử (Multi-Agent) cho quán coffee Highlands với khả năng hội thoại tự nhiên, tư vấn thông minh và xử lý đặt hàng tự động.

## 🏗️ Kiến trúc hệ thống

### Phần A: Router Agent (60%)
- **Router Agent**: Phân loại câu hỏi và routing đến agent phù hợp
- **Training Data**: Dataset đa dạng cho việc huấn luyện router
- **Fine-tuning**: Tối ưu hóa model router với LoRA

### Phần B: Graph RAG & LLMServing (40%)
- **Neo4j Graph Database**: Cơ sở tri thức với vector indexes
- **Hybrid Search**: Kết hợp vector search và graph traversal
- **LLM Serving**: vLLM với streaming responses
- **Multi-layer Caching**: Redis semantic cache

## 🤖 Các Agents

1. **🎯 Router Agent**: Phân loại và chuyển tiếp câu hỏi
2. **❓ FAQ Agent**: Trả lời câu hỏi thường gặp
3. **💬 Consultant Agent**: Tư vấn menu và dịch vụ
4. **🛒 Order Agent**: Xử lý đặt hàng và thanh toán

## 🚀 Quick Start - Chat Demo

### Cách chạy nhanh nhất:

```bash
# 1. Khởi động toàn bộ hệ thống
python launch_demo.py

# 2. Demo sẽ tự động mở trong trình duyệt
```

### Manual Setup:

```bash
# 1. Khởi động services
docker-compose -f docker/docker-compose.yml up -d

# 2. Setup database
PYTHONPATH=. python scripts/setup_neo4j_schema.py

# 3. Ingest dữ liệu
PYTHONPATH=. python scripts/ingest_data.py

# 4. Khởi động API server
PYTHONPATH=. python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 5. Mở chat_demo.html trong trình duyệt
```

## 💬 Demo Scenarios

### 1. FAQ Questions
```
User: Wifi password là gì?
→ Router → FAQ Agent: Highlands123

User: Quán mở cửa từ mấy giờ?
→ Router → FAQ Agent: 7h sáng - 10h tối
```

### 2. Menu Consultation
```
User: Các loại coffee của quán?
→ Router → Consultant Agent: Latte, Americano, Mocha...

User: Latte có giá bao nhiêu?
→ Router → Consultant Agent: 49,000 VND
```

### 3. Order Processing
```
User: Tôi muốn đặt 2 ly latte
→ Router → Order Agent: Xử lý đơn hàng...
```

## 📊 Performance Metrics

- **TTFT (Time to First Token)**: ≤ 0.2s
- **Token Throughput**: 50-100 tokens/s
- **Multi-turn Context**: Giữ ngữ cảnh cuộc hội thoại
- **Agent Routing Accuracy**: >95%

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Web framework với async support
- **Neo4j**: Graph database cho knowledge base
- **Redis**: Multi-layer caching
- **vLLM**: LLM serving với streaming
- **Sentence Transformers**: Embeddings và reranking

### Frontend
- **HTML/CSS/JavaScript**: Chat UI với streaming
- **Server-Sent Events**: Real-time token streaming
- **Responsive Design**: Mobile-friendly

### Infrastructure
- **Docker Compose**: Container orchestration
- **GPU Support**: CUDA cho LLM inference
- **Async Processing**: Non-blocking operations

## 📁 Project Structure

```
├── app/                          # FastAPI application
│   ├── agents/                   # Agent implementations
│   ├── rag/                      # RAG components
│   ├── serving/                  # LLM serving
│   ├── cache/                    # Caching layer
│   └── utils/                    # Utilities
├── training/                     # Router training
├── docker/                       # Docker configs
├── scripts/                      # Setup scripts
├── data/                         # Training data
├── chat_demo.html               # Chat UI demo
├── launch_demo.py               # Demo launcher
└── requirements.txt             # Python dependencies
```

## 🔧 Development Setup

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Node.js (optional, for frontend dev)
- GPU với CUDA (recommended)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd multi-agent-fb-ai

# Install Python dependencies
pip install -r requirements.txt

# Install router dependencies
pip install -r requirements_router.txt
```

### Database Setup

```bash
# Start Neo4j
docker-compose -f docker/docker-compose.yml up neo4j -d

# Setup schema
PYTHONPATH=. python scripts/setup_neo4j_schema.py

# Ingest data
PYTHONPATH=. python scripts/ingest_data.py
```

### Training Router (Optional)

```bash
# Generate training data
PYTHONPATH=. python training/generate_router_data.py

# Train router model
PYTHONPATH=. python training/train_router.py
```

## 🧪 Testing

```bash
# Run unit tests
python -m pytest

# Test router inference
PYTHONPATH=. python -m pytest test_router.py

# Benchmark performance
PYTHONPATH=. python benchmark.py
```

## 📈 Monitoring & Metrics

- **API Health**: `GET /health`
- **Performance Benchmark**: `GET /benchmark`
- **Chat Endpoint**: `POST /chat`
- **API Documentation**: `GET /docs`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🎉 Acknowledgments

- Neo4j for graph database
- vLLM for efficient LLM serving
- Sentence Transformers for embeddings
- FastAPI for web framework

---

## 📞 Support

For questions or issues:
- Check the [CHAT_DEMO_README.md](CHAT_DEMO_README.md) for detailed demo instructions
- Review [troubleshooting guide](#troubleshooting) in demo README
- Open an issue on GitHub

---

*Built with ❤️ for intelligent coffee shop conversations*