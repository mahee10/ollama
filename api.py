import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import ollama
from fastapi import FastAPI
from pydantic import BaseModel

MODEL = "llama3.2:1b"
CHAT_SYSTEM_PROMPT = (
    "You are a helpful travel assistant that can customize travel plans "
    "to make for a great getaway."
)
WEATHER_SYSTEM_PROMPT = (
    "You are a agent that can use tools to get information about the weather "
    "in a city. Your answer to a city's weather should consist of the day of "
    "week and the high and low temperatures only, and the response should be "
    "given in plain english."
)

CBUS_GUIDE_PATH = Path(__file__).parent / "CBUS2025.txt"

app = FastAPI(title="Ollama Local API")


@app.get("/")
def root():
    return {
        "name": app.title,
        "docs": "/docs",
        "endpoints": [
            {
                "method": "POST",
                "path": "/chat",
                "description": "Basic travel chat (Ollama.py style)",
                "body": {"message": "your question"},
            },
            {
                "method": "POST",
                "path": "/rag",
                "description": "Chat grounded in CBUS2025.txt",
                "body": {"message": "your question"},
            },
            {
                "method": "POST",
                "path": "/weather",
                "description": "Weather via tool calling (wttr.in)",
                "body": {"city": "Columbus"},
            },
        ],
    }


class ChatRequest(BaseModel):
    message: str


class RagRequest(BaseModel):
    message: str


class WeatherRequest(BaseModel):
    city: str


def get_current_weather(city: str) -> dict:
    try:
        url = f"https://wttr.in/{city}?format=j1"
        with urlopen(url) as response:
            data = json.loads(response.read().decode())
        current = data.get("current_condition", [{}])[0]
        return {
            "temperature": current.get("temp_C", "N/A"),
            "condition": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
        }
    except (HTTPError, URLError, json.JSONDecodeError, IndexError):
        return {"error": "Failed to fetch weather data"}


weather_tool = {
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city",
                },
            },
            "required": ["city"],
        },
    },
}

available_functions = {"get_current_weather": get_current_weather}


def load_rag_system_prompt() -> str:
    document_text = CBUS_GUIDE_PATH.read_text(encoding="utf-8")
    return (
        "You are a helpful travel assistant that can customize travel plans "
        f"to make for a great getaway. Exclusively use the following information "
        f"to inform your response: {document_text}"
    )


@app.post("/chat")
def chat(req: ChatRequest):
    messages = [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT},
        {"role": "user", "content": req.message},
    ]
    response = ollama.chat(model=MODEL, messages=messages)
    return {"content": response["message"]["content"]}


@app.post("/rag")
def rag(req: RagRequest):
    messages = [
        {"role": "system", "content": load_rag_system_prompt()},
        {"role": "user", "content": req.message},
    ]
    response = ollama.chat(model=MODEL, messages=messages)
    return {"content": response["message"]["content"]}


@app.post("/weather")
def weather(req: WeatherRequest):
    messages = [
        {"role": "system", "content": WEATHER_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"What is the weather in {req.city} for next Tuesday?",
        },
    ]
    response = ollama.chat(
        model=MODEL,
        messages=messages,
        tools=[weather_tool],
        options={"temperature": 0.1},
    )

    tool_data = None
    if "tool_calls" in response["message"]:
        messages.append(response["message"])
        for tool_call in response["message"]["tool_calls"]:
            function_name = tool_call["function"]["name"]
            function_args = tool_call["function"]["arguments"]
            if isinstance(function_args, str):
                function_args = json.loads(function_args)
            if function_name == "get_current_weather":
                city = function_args.get("city") or req.city
                tool_data = get_current_weather(city)
            elif function_to_call := available_functions.get(function_name):
                tool_data = function_to_call(**function_args)
            else:
                continue
            messages.append(
                {
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(tool_data),
                }
            )
        final_response = ollama.chat(model=MODEL, messages=messages)
        return {
            "content": final_response["message"]["content"],
            "weather": tool_data,
        }

    return {
        "content": response["message"]["content"],
        "weather": tool_data,
    }
