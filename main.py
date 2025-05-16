from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, RunConfig, ItemHelpers, function_tool
from agents.extensions.models.litellm_model import LitellmModel
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
from tavily import TavilyClient
import os
import asyncio
import httpx
from typing import AsyncGenerator, Dict, Any

# Load environment variables
load_dotenv()

# Disable tracing
set_tracing_disabled(True)

# Initialize FastAPI app
app = FastAPI(
    title="Customized Chatbot",
    description="A FastAPI-based API for Customized Chatbot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the model
my_model = LitellmModel(api_key=os.getenv("GEMINI_API_KEY"), model="gemini/gemini-2.0-flash")

# Create weather search tool
@function_tool
def weather_tool(user_input: str) -> str:
    """Search tool for weather information"""
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = tavily_client.search(query=user_input)
    return response

# Create Serper search tool
@function_tool
async def serper_search(query: str) -> str:
    """Search tool using Serper API for general web search"""
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "gl": "us",
        "hl": "en"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Extract relevant information from the response
            if "organic" in data:
                results = []
                for result in data["organic"][:3]:  # Get top 3 results
                    results.append(f"Title: {result.get('title', 'N/A')}\n"
                                 f"Link: {result.get('link', 'N/A')}\n"
                                 f"Snippet: {result.get('snippet', 'N/A')}\n")
                return "\n\n".join(results)
            return "No search results found."
        else:
            return f"Error: {response.status_code} - {response.text}"

# Initialize the agent with both tools
agent = Agent(
    name="Assistant",
    instructions="""You are a powerful and intelligent AI assistant with access to multiple tools and data sources. Your capabilities include:
Web Search: Use the serper_search tool to answer general knowledge or current event questions by searching the internet.
Weather Information: Use the weather_tool to provide accurate and up-to-date weather information when asked.
Math Solving: Accurately solve mathematical problems and explain the steps or reasoning where helpful.
GitHub Repo Knowledge: You have full knowledge of the GitHub repository https://github.com/panaversity/learn-agentic-ai  ,   https://github.com/panaversity/learn-agentic-ai?tab=readme-ov-file#readme. You can answer any question related to the content of this repo, including code, concepts, structure, and tutorials inside it.
📌 When the user asks "answer all questions", respond to all types of questions — general, mathematical, weather-related, or related to the GitHub repo — using the most relevant tools and sources.
Your job is to:
Understand the user's query clearly.
Use the appropriate tools or data (web, math logic, weather, or the Agentic AI GitHub repo) to answer.
Always respond with complete, helpful, and accurate information.""",
    model=my_model,
    tools=[weather_tool, serper_search]  # Add both tools to the agent
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Gemini Chat API! Use /chat for chat endpoint and /chat/stream for streaming responses."}

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Collect the response
    full_response = ""
    result = Runner.run_streamed(starting_agent=agent, input=request.message)
    
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            full_response += event.data.delta
    
    return ChatResponse(response=full_response)

# Streaming chat endpoint
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    async def generate():
        result = Runner.run_streamed(starting_agent=agent, input=request.message)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                yield event.data.delta

    return StreamingResponse(generate(), media_type="text/plain")

