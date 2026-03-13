"""
Gemini chat service with async client + function calling.
"""

import asyncio
import json
from datetime import datetime
from loguru import logger
from google.genai import types
from utils.ai_coversation import aclient, ai_model


# ─── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_current_datetime",
                description="Get the current date and time",
                parameters=types.Schema(type=types.Type.STRING, properties={}),
            ),
            # types.FunctionDeclaration(
            #     name="get_weather",
            #     description="Get current weather for a city (placeholder - returns mock data)",
            #     parameters=types.Schema(
            #         type=types.Type.OBJECT,
            #         properties={
            #             "city": types.Schema(
            #                 type=types.Type.STRING, description="City name"
            #             )
            #         },
            #         required=["city"],
            #     ),
            # ),
        ]
    )
]


async def _execute_tool(
    tool_name: str, tool_args: dict, user_id: str, guild_id: str, aclient
) -> str:
    """Execute a tool call and return result as string."""
    try:
        if tool_name == "get_current_datetime":
            now = datetime.now()
            return f"Bây giờ là {now.strftime('%A')} {now.strftime('%Y-%m-%d %H:%M:%S')} UTC"

        elif tool_name == "get_weather":
            city = tool_args.get("city", "")
            return json.dumps(
                {
                    "city": city,
                    "temperature": "25°C",
                    "condition": "Partly Cloudy",
                    "humidity": "65%",
                    "note": "Mock data. Integrate a real weather API for production.",
                }
            )

        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    except Exception as e:
        logger.error(f"Tool execution error ({tool_name}): {e}")
        return json.dumps({"error": str(e)})


async def generate_response(
    user_message: str,
    history: list[dict],
    user_facts: list[str],
    user_id: str,
    guild_id: str,
    username: str = "User",
) -> str:
    """Generate a response using async Gemini client with tool calling."""

    facts_text = (
        "\n".join(f"- {f}" for f in user_facts) if user_facts else "None stored yet."
    )
    system_prompt = f"""You are a helpful, friendly Discord bot assistant.
You have memory of this user and can use tools when needed.

User: {username} (ID: {user_id})

Facts you know about this user:
{facts_text}

## Response style:
- Default language is Vietnamese. Answer in Vietnamese except there are request to answer in other language
- No need to be formal. Just match their tone—whatever they call you, call them right back.
- Be honest when you don't know something
- Keep responses under 2000 characters to fit Discord limits
- No swear and example any swear word
- No yapping

## Thinking Guidelines:
- Simple questions (greetings, basic facts, casual chat) → reply directly, no need to overthink
- Explanations, comparisons, simple code → think moderately
- Math problems, complex debugging, multi-step logic, proofs → think carefully and thoroughly before answering

## Tools use guidelines:
- Only use tools when truly necessary (data lookup, executing specific actions). For general questions, respond directly without calling any tools.
- Use the search_files tool when users ask about their uploaded documents
"""

    # Build message history for Gemini
    gemini_contents = []
    for msg in history[-10:]:
        role = "user" if msg["role"] == "user" else "model"
        gemini_contents.append(
            types.Content(role=role, parts=[types.Part(text=msg["content"])])
        )

    gemini_contents.append(
        types.Content(role="user", parts=[types.Part(text=user_message)])
    )

    # Async client + agentic tool loop
    response = await aclient.models.generate_content(
        model=ai_model,
        contents=gemini_contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            tools=TOOLS,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="AUTO")
            ),
            temperature=0.7,
        ),
    )

    function_calls = response.function_calls

    if not function_calls:
        return (
            response.text
            or "I processed your request but couldn't formulate a final response."
        )

    # Execute all tool calls concurrently
    tool_results = await asyncio.gather(
        *[
            _execute_tool(
                func.name,
                dict(func.args),
                user_id,
                guild_id,
                aclient,
            )
            for func in function_calls
        ]
    )
    return str(tool_results)
