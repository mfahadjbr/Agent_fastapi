# Customized Chatbot API

A powerful FastAPI-based chatbot that combines multiple AI capabilities including web search, weather information, and specialized knowledge about Agentic AI.

## Features

- 🤖 Powered by Gemini 1.5 Flash model
- 🔍 Web search capabilities using Serper API
- 🌤️ Weather information using Tavily API
- 📚 Specialized knowledge about Agentic AI
- ⚡ Streaming response support
- 🔄 Real-time chat interactions

## Prerequisites

- Python 3.10 or higher
- FastAPI
- Uvicorn
- Required API keys:
  - Gemini API key
  - Serper API key
  - Tavily API key


2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn python-dotenv httpx tavily-python
```

4. Create a `.env` file in the root directory with your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key
SERPER_API_KEY=your_serper_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## Running the Application

Start the server with:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Root Endpoint
```http
GET /
```
Returns a welcome message and basic API information.

### 2. Chat Endpoint
```http
POST /chat
```
Regular chat endpoint that returns complete responses.

**Request Body:**
```json
{
    "message": "Your question or message here"
}
```

**Response:**
```json
{
    "response": "AI's response to your message"
}
```

### 3. Streaming Chat Endpoint
```http
POST /chat/stream
```
Streaming endpoint that returns responses in real-time.

**Request Body:**
```json
{
    "message": "Your question or message here"
}
```

## Example Usage

### Using curl

1. Regular chat:
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is Agentic AI?"}'
```

2. Streaming chat:
```bash
curl -X POST "http://localhost:8000/chat/stream" \
     -H "Content-Type: application/json" \
     -d '{"message": "Tell me about the weather in New York"}'
```

### Using Python

```python
import requests

# Regular chat
response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "What is Agentic AI?"}
)
print(response.json()["response"])

# Streaming chat
response = requests.post(
    "http://localhost:8000/chat/stream",
    json={"message": "Tell me about the weather in New York"},
    stream=True
)
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Features in Detail

1. **Web Search**
   - Uses Serper API for real-time web search
   - Returns top 3 most relevant results
   - Includes titles, links, and snippets

2. **Weather Information**
   - Powered by Tavily API
   - Provides accurate weather data
   - Supports location-based queries

3. **Agentic AI Knowledge**
   - Specialized knowledge about the Agentic AI repository
   - Can answer questions about code, concepts, and tutorials
   - Based on the repository: https://github.com/panaversity/learn-agentic-ai

## Error Handling

The API includes proper error handling for:
- Empty messages
- Invalid API keys
- Network issues
- Server errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
