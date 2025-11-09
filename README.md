# 🧣 AI Assistant for Scarf Brand

## About

This innovative project offers an intelligent conversational assistant specifically designed for a luxury scarf brand. By combining advanced AI technologies, it provides a personalized and intuitive shopping experience via WhatsApp.

### 🎯 Mission

Our assistant revolutionizes customer interaction by offering:

- Detailed analysis of scarves using computer vision
- Natural and contextual conversations in multiple languages
- Personalized recommendations based on preferences
- Transparent management of transactions and inventory

### 💡 Technical Innovation

The project stands out for:

- A sophisticated multi-agent architecture for optimal scalability
- Multimodal processing (images, text, voice) for a seamless user experience
- A modern event-driven infrastructure with Redis
- Advanced vector search for precise recommendations

### 🔍 Key Points

- **Performance**: Response time < 2s for all interactions
- **Scalability**: Distributed architecture supporting >10k simultaneous users
- **Accuracy**: >95% accuracy in pattern recognition
- **Security**: End-to-end encryption and GDPR compliance

## ✨ Features

- 📱 **WhatsApp Integration**: Natural messaging interface
- 🖼️ **Image Analysis**: Scarf recognition and feature extraction
- 🗣️ **Voice Processing**: Voice message support
- 🤖 **Natural Dialog**: Contextual and personalized responses
- 📦 **Inventory Management**: Real-time stock verification
- 💳 **Transactions**: Integrated purchase process
- 🎯 **Recommendations**: Personalized suggestions
- 🔄 **Virtual Try-On**: AR-based scarf visualization
- 👗 **Style Advisor**: Personal styling recommendations
- 📈 **Trend Analysis**: Real-time fashion trend insights
- 🎨 **Color Matching**: Intelligent color harmony suggestions
- 🌤️ **Seasonal Recommendations**: Weather-aware style advice

## 🏗️ Architecture

### System Overview

![System Architecture](System_Architecture.png)

### Specialized Agents

- `VisionAgent`: Product image analysis and feature extraction
- `DialogAgent`: Natural language understanding and generation
- `InventoryAgent`: Stock management and availability tracking
- `TransactionAgent`: Order processing and payment handling

### Technologies

- 🐍 **Backend**: Python with FastAPI
- 🤖 **AI**:
  - Local: Mistral-7B (default)
  - Cloud: OpenRouter (Gemini-2.5-pro) optional
  - Vision: BLIP-2 / CLIP
- 🔄 **Communication**: MCP (Model Context Protocol)
- 🗄️ **Storage**:
  - PostgreSQL (structured data)
  - Redis (cache and pub/sub)
  - FAISS/Weaviate (vector search)

## 🚀 Installation

1. **Clone the repository**

```bash
git clone https://github.com/asmamest/Scarf-Brand-Assistant.git
cd Scarf-Brand-Assistant
```

2. **Configure environment**

```bash
# Copy example file
cp .env.example .env

# Edit with your configurations
nano .env
```

3. **Launch with Docker**

```bash
docker-compose up -d
```

4. **Manual installation (alternative)**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or 'venv\Scripts\activate' on Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
./setup.sh
```

## ⚙️ Configuration

### AI Model Options

1. **Local (default)**

```env
MODEL_PROVIDER=local
MODEL_NAME=mistral-7b-instruct
```

2. **OpenRouter (Gemini)**

```env
MODEL_PROVIDER=openrouter
MODEL_NAME=google/gemini-2.5-pro
OPENROUTER_API_KEY=your_key
```

3. **OpenAI**

```env
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4
OPENAI_API_KEY=your_key
```

### Vector Store

```env
# FAISS (local, default)
VECTOR_STORE=faiss

# Weaviate
VECTOR_STORE=weaviate
VECTOR_STORE_URL=http://localhost:8080
```

## 📊 Monitoring

- **Prometheus**: System metrics (port 9090)
- **Grafana**: Visualization (port 3000)

## 🔒 Security

- Encryption of sensitive data
- Customer consent management
- Automatic media cleanup after processing
- Temporary access tokens

## 🧪 Tests

```bash
# Unit tests
pytest

# Coverage tests
pytest --cov=src/
```

## 📝 Usage Examples

### WhatsApp Webhook

```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "image",
      "image": {
        "url": "https://example.com/scarf.jpg"
      }
    },
    "customer": {
      "id": "123"
    }
  }'
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Support

For questions or support:

- Open an issue
- Contact the development team

---

Built with ❤️
