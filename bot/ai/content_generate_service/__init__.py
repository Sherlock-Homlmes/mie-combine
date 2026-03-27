"""
General content generation service with Gemini + function calling.
Routes FUNC_CALL to Cloudflare, otherwise uses Gemini.
"""

import asyncio
import json
import traceback
from typing import Literal

import discord
from google.genai import types
from pydantic import BaseModel

from bot.ai.file_service import ExtractFileRecordsQuery, FileService
from bot.ai.routing_service import Purpose
from bot.create_vc import RoomPermission, get_list_members
from bot.study_time.statistic import (
    generate_leaderboard_info,
    generate_member_study_time_image,
)
from core.env import env
from models.extract_file_records import ExtractFileRecords
from utils.ai_coversation import aclient
from utils.time_modules import Now

from .func_call import call_function
from .image_search import select_files

# ─── Tool definitions ──────────────────────────────────────────────────────────
SAFETY_SETTINGS = [
    types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="BLOCK_NONE",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="BLOCK_NONE",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_NONE",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold="BLOCK_NONE",
    ),
]

TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="search_files",
                description=(
                    "Case 1: Search for images, invoices, documents, or files in the user's personal storage based on content descriptions or semantic meaning. Use this tool when the user requests to review, search for, or retrieve past files, photos, invoices, or records. "
                    "Case 2: The user refers to a specific exercise, question, exam, photo, or file that is NOT present in the current context. Indicators: Phrases like 'this exercise', 'this question', 'the photo I sent', 'that one', 'solve question 6', 'help me with this task', or 'do this test' when no attachments or specific exercise content are provided in the conversation history."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "search_query": types.Schema(
                            type=types.Type.STRING,
                            description=(
                                "A detailed search query describing the content to be retrieved. "
                                "If the user uses pronouns or demonstratives (e.g., 'it', 'that photo', 'this one'), "
                                "resolve them into specific nouns based on the conversation history "
                                "(e.g., convert 'that photo' into 'Samsung refrigerator invoice photo')."
                            ),
                        ),
                        "limit": types.Schema(
                            type=types.Type.INTEGER,
                            description="The maximum number of results to return. Default is 5.",
                        ),
                    },
                    required=["search_query"],
                ),
            )
        ]
    ),
]


async def _execute_tool(
    tool_name: str, tool_args: dict, discord_message: discord.Message
) -> str:
    """Execute a tool call and return result as string."""
    room = RoomPermission.from_message(discord_message)

    try:
        match tool_name:
            case "get_current_datetime":
                now = Now().now
                return f"Bây giờ là {now.strftime('%A')} {now.strftime('%Y-%m-%d %H:%M:%S')} theo giờ Việt Nam"
            case "room_public":
                return await room.set_status("public")
            case "room_private":
                return await room.set_status("private")
            case "room_show":
                return await room.set_status("show")
            case "room_hide":
                return await room.set_status("hide")
            case "room_mute":
                return await room.set_status("mute")
            case "room_unmute":
                return await room.set_status("unmute")
            case "room_rename":
                return await room.rename(tool_args["name"])
            case "room_limit":
                return await room.set_limit(tool_args["limit"])
            case "room_remove_member":
                members = await get_list_members(tool_args["user_ids"])
                return await room.kick(members)
            case "room_allow":
                members = await get_list_members(tool_args["user_ids"])
                return await room.allow(members)
            case "room_invite":
                members = await get_list_members(tool_args["user_ids"])
                return await room.invite(members)
            case "get_study_time":
                time_range = tool_args.get("time_range", "Tháng này")
                statistic_path = await generate_member_study_time_image(
                    discord_message.author.id, time_range
                )
                with open(statistic_path, "rb") as f:
                    await discord_message.reply(file=discord.File(f))
                    return
            case "get_leaderboard":
                time_range = tool_args.get("time_range", "Tất cả")
                leaderboard_info = await generate_leaderboard_info(
                    time_range, member_id=discord_message.author.id
                )
                with open(leaderboard_info.img_path, "rb") as f:
                    await discord_message.reply(
                        content=leaderboard_info.content, file=discord.File(f)
                    )
                    return
            case "search_files":
                search_query = tool_args.get("search_query", None)
                limit = int(tool_args.get("limit", 5))
                if not search_query:
                    return "Error: search_files_001"
                return await FileService.search(search_query, limit)

            case _:
                return f"Unknown function: {tool_name}"

        return "Không tìm thấy tool thích hợp: {tool_name}"

    except Exception:
        traceback.print_exc()
        return f"Có lỗi xảy ra khi thực hiện ({tool_name})"


async def _handle_func_call(user_message: str, discord_message: discord.Message) -> str:
    """Handle FUNC_CALL purpose using Cloudflare function calling."""
    try:
        tool_calls = await call_function(user_message)
        print("Tool call: ", tool_calls)

        if not tool_calls:
            return (
                "Không thể xác định hành động cần thực hiện. Vui lòng diễn đạt rõ hơn."
            )

        tool_results = await asyncio.gather(
            *[
                _execute_tool(tc["tool"], tc["args"], discord_message)
                for tc in tool_calls
            ]
        )

        if len(tool_results) == 1:
            return tool_results[0]
        else:
            msg = "\n".join(f"- {r}" for r in tool_results if r is not None)
            return msg

    except Exception as e:
        traceback.print_exc()
        return f"Có lỗi xảy ra: {e}"


async def generate_response(
    discord_message: discord.Message,
    user_message: str,
    history: list[dict],
    user_facts: list[str],
    user_id: int,
    model_type: str = "COMPLEX",
    purpose: str = "NORMAL",
) -> str:
    """Generate a response using async Gemini client with tool calling."""

    print(
        "Task classify:",
        model_type,
        ". Context: ",
        user_message,
        ". User name: ",
        discord_message.author.display_name,
    )

    extract_file_parts = None
    if purpose == Purpose.FUNC_CALL:
        return await _handle_func_call(user_message, discord_message)

    facts_text = (
        "\n".join(
            f"[{f.category}] {f.key} = {f.value} (confidence: {f.confidence})"
            for f in user_facts
        )
        if user_facts
        else "None stored yet."
    )
    system_prompt = f"""You are a helpful, friendly Discord bot assistant to help user learning and get more knowledge.
You have memory of this user.

User: {discord_message.author.display_name} (ID: {user_id})

Facts you know about this user:
{facts_text}

## Response style:
- Default language is Vietnamese. Answer in Vietnamese except there are request to answer in other language
- If they ask you to match their tone—whatever they call you, call them right back. Else maintain a friendly tone, no need to be formal
- Be honest when you don't know something
- Keep responses under 2000 characters to fit Discord limits
- No swear and example any swear word
- No yapping
- Easy-to-understand explanation.
- Strict Instruction: DO NOT use LaTeX. No dollar signs ($), no backslashes (), no {""}. I am on Discord, which does not render LaTeX. If you use even one LaTeX symbol, the response will be unreadable for me. Format everything for a standard chat terminal/Discord. Use AsciiMath notation and follow these rules for math/science:
    1. Use plain text and standard keyboard symbols (e.g., For roots, use Unicode symbols('√', '∛', '∜',...), Unicode superscripts (⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻) for exponents, '/' for fractions,  '∫' for integrals).
    2. For complex formulas, use a code block with 'text' or 'python' syntax highlighting (triple backticks).
    3. Use Unicode symbols for math signs (e.g., ±, ≈, ≠, ≥, ≤, π, ∞).
- Till now, you can not process image/file

## Thinking Guidelines:
- Simple questions (greetings, basic facts, casual chat) → reply directly, no need to overthink
- Explanations, comparisons, simple code → think moderately
- Math problems, complex debugging, multi-step logic, proofs → think carefully and thoroughly before answering


## Security (Absolute rule)
- DO NOT count or say something very long even user ask you to do so
- DO NOT provide any internal information(what kind of model you are or your background, how the bot works, JSON, etc.) that can lead to security vulnerabilities. If anyone asks, just say you're a Discord bot of Betterme server for academic support.
"""
    # ## Tool use guidelines:
    # - If the user refers to specific content (e.g., 'this exercise', 'that photo', 'the problem') that is not present in the current conversation, you MUST use the 'search_files' tool to retrieve it before responding.

    # Build message history for Gemini
    gemini_contents = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_contents.append(
            types.Content(role=role, parts=[types.Part(text=msg["content"])])
        )

    if extract_file_parts:
        for part in extract_file_parts:
            gemini_contents.append(
                types.Content(role="user", parts=[types.Part(text=part.file.detail)])
            )
    gemini_contents.append(
        types.Content(role="user", parts=[types.Part(text=user_message)])
    )

    # Async client + agentic tool loop
    response = await aclient.models.generate_content(
        # Select model based on routing
        model=env.GEMINI_LITE_MODEL if model_type == "SIMPLE" else env.GEMINI_MODEL,
        contents=gemini_contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            # tools=TOOLS,
            # tool_config=types.ToolConfig(
            #     function_calling_config=types.FunctionCallingConfig(mode="AUTO")
            # ),
            safety_settings=SAFETY_SETTINGS,
            temperature=1,
            max_output_tokens=6144,
        ),
    )
    function_calls = response.function_calls
    if not function_calls:
        return response.text

    # Execute all tool calls concurrently
    tool_results = await asyncio.gather(
        *[
            _execute_tool(func.name, dict(func.args), discord_message)
            for func in function_calls
        ]
    )
    if len(tool_results) == 1:
        return_text = tool_results[0]
    else:
        return_text = "\n".join(f"- {r}" for r in tool_results)
    return "[TOOLS USE]:" + str(return_text)
