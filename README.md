# 🤖 Multi-Persona Chatbot

A FastAPI-based AI chatbot that can adopt multiple personas (Teacher, Doctor, Friend) to provide personalized conversational experiences. Built with Ollama for local LLM inference and includes comprehensive safety features.

## ✨ Features

- **Multiple Personas**: Switch between Teacher, Doctor, and Friend personas
- **Local LLM Inference**: Uses Ollama with lightweight models (no cloud dependency)
- **Safety First**: 
  - Input validation and sanitization
  - Injection attack prevention
  - Harmful content filtering
  - Persona-specific safety guardrails
  - Medical disclaimers for doctor persona
- **Real-time Chat**: WebSocket-ready architecture
- **Clean API**: RESTful endpoints with strict validation
- **Conversation History**: Maintains context across messages

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- Ollama model pulled: `qwen2:0.5b` (or configure your own)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mr-reyansh/Multi-Persona_chatbot.git
   cd Multi-Persona_chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Ollama service**
   ```bash
   ollama serve
   ```

5. **Pull the model (in another terminal)**
   ```bash
   ollama pull qwen2:0.5b
   ```

6. **Run the application**
   ```bash
   python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the application**
   - UI: http://localhost:8000
   - Chat: http://localhost:8000/chat
   - Health: http://localhost:8000/health

## 📋 Project Structure

```
├── backend/
│   ├── app.py              # FastAPI application with endpoints
│   ├── llm_service.py      # Ollama integration and response generation
│   └── safety.py           # Safety validation and content filtering
├── static/
│   ├── css/
│   │   └── style.css       # Frontend styling
│   └── js/
│       └── app.js          # Frontend logic
├── templates/
│   ├── index.html          # Landing page
│   └── chat.html           # Chat interface
├── .gitignore              # Git ignore rules
├── Procfile                # Heroku deployment config
├── requirements.txt        # Python dependencies
├── PRECAUTIONS.md          # Safety documentation
├── deployment_guide.md     # Deployment instructions
└── README.md               # This file
```

## 🧠 Personas

### Teacher
- Structured, educational responses
- Step-by-step explanations
- Simple but comprehensive

### Doctor
- Professional and clinical tone
- Includes medical disclaimers
- Supportive communication

### Friend
- Casual and warm tone
- Empathetic support
- Conversational style

## 🔒 Safety Features

The application includes comprehensive safety precautions:

- **Input Validation**: Message length, type, and format validation
- **Injection Prevention**: Detects and blocks XSS, template injection, code execution
- **Content Filtering**: Blocks self-harm, violence, illegal content, hate speech
- **Sanitization**: Removes HTML tags and dangerous patterns
- **Response Guardrails**: Validates response quality and enforces disclaimers
- **Error Handling**: Comprehensive error messages and logging
- **CORS Security**: Whitelisted origins and method restrictions

For detailed safety documentation, see [PRECAUTIONS.md](PRECAUTIONS.md).

## 📡 API Endpoints

### GET `/`
Returns the landing page.

### GET `/chat`
Returns the chat interface.

### POST `/api/chat`
Main chat endpoint.

**Request:**
```json
{
  "message": "What is photosynthesis?",
  "persona": "teacher",
  "history": [
    {"role": "User", "content": "Hi"},
    {"role": "Assistant", "content": "Hello!"}
  ]
}
```

**Response:**
```json
{
  "response": "Photosynthesis is the process...",
  "safety_checked": true
}
```

**Valid Personas**: `teacher`, `doctor`, `friend`

**Parameters:**
- `message` (required): 1-1000 characters
- `persona` (required): One of the valid personas
- `history` (optional): Array of previous messages (max 50)

### GET `/health`
Health check endpoint.

## 🛠️ Configuration

Create a `.env` file in the root directory:

```env
# Ollama Configuration
OLLAMA_URL=http://localhost:11434/api/generate
MODEL_NAME=qwen2:0.5b
REQUEST_TIMEOUT=60

# Server Configuration
PORT=8000
LOG_LEVEL=INFO

# CORS Configuration (update as needed)
ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000
```

## 📦 Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **httpx** - Async HTTP client
- **pydantic** - Data validation
- **jinja2** - Template engine
- **python-dotenv** - Environment variables
- **slowapi** - Rate limiting

## 🚀 Deployment

### Heroku
```bash
git push heroku main
```

See [deployment_guide.md](deployment_guide.md) for detailed instructions.

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧪 Testing

### Test Safety Features

```bash
# Test input validation
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"test","persona":"invalid"}'

# Test harmful content blocking
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"<script>alert(1)</script>","persona":"friend"}'

# Test normal operation
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","persona":"friend"}'
```

See [PRECAUTIONS.md](PRECAUTIONS.md) for comprehensive testing guide.

## 📝 Logging

The application logs important events:
- Request/response pairs
- Model generation
- Errors and exceptions
- Security events (blocked requests)

Access logs in console output or configure external logging service.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔐 Security

For security vulnerabilities, please email: **security@multipersona-chatbot.dev**

Do not create public GitHub issues for security vulnerabilities.

See [PRECAUTIONS.md](PRECAUTIONS.md) for security checklist and best practices.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Pydantic](https://docs.pydantic.dev/) for data validation

## 📞 Support

For questions and support:
- Open an issue on GitHub
- Check existing documentation in [PRECAUTIONS.md](PRECAUTIONS.md)
- Review [deployment_guide.md](deployment_guide.md)

## 🗺️ Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Advanced NLP-based content moderation
- [ ] User authentication and session management
- [ ] Database integration for conversation history
- [ ] Multi-language support
- [ ] Performance optimizations
- [ ] Mobile-friendly UI improvements
- [ ] Admin dashboard for monitoring

---

**Last Updated**: April 7, 2026

Made with ❤️ by the Multi-Persona Chatbot Team
