"""
Gemini chat service with async client + function calling.
"""

import asyncio
import traceback

import discord
from google.genai import types

from bot.create_vc.funcs import RoomPermission, get_list_members

# from loguru import logger
from core.env import env
from utils.ai_coversation import aclient
from utils.time_modules import Now

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
                name="get_current_datetime",
                description="Lấy thời gian hiện tại. Chỉ gọi khi chắc chắn người ta muốn xem thời gian hiện tại, không cần thiết phải trả lời các câu hỏi liên quan đến thời gian bằng tool này",
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
            types.FunctionDeclaration(
                name="room_public",
                description="Cho phép mọi người vào phòng",
                parameters=types.Schema(type=types.Type.OBJECT, properties={}),
            ),
            types.FunctionDeclaration(
                name="room_private",
                description="Không cho phép mọi người vào phòng",
                parameters=types.Schema(type=types.Type.OBJECT, properties={}),
            ),
            types.FunctionDeclaration(
                name="room_show",
                description="Phòng đang bị ẩn. Hiển thị phòng cho mọi người thấy",
                parameters=types.Schema(type=types.Type.OBJECT, properties={}),
            ),
            types.FunctionDeclaration(
                name="room_hide",
                description="Ẩn phòng không cho mọi người thấy",
                parameters=types.Schema(type=types.Type.OBJECT, properties={}),
            ),
            types.FunctionDeclaration(
                name="room_mute",
                description="Tắt âm phòng",
                parameters=types.Schema(type=types.Type.OBJECT, properties={}),
            ),
            types.FunctionDeclaration(
                name="room_unmute",
                description="Bật âm thanh phòng",
                parameters=types.Schema(type=types.Type.OBJECT, properties={}),
            ),
            types.FunctionDeclaration(
                name="room_rename",
                description="Đổi tên phòng",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "name": types.Schema(
                            type=types.Type.STRING, description="Tên mới của phòng"
                        )
                    },
                    required=["name"],
                ),
            ),
            types.FunctionDeclaration(
                name="room_limit",
                description="Đặt giới hạn số người trong phòng",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "limit": types.Schema(
                            type=types.Type.INTEGER, description="Số người tối đa"
                        )
                    },
                    required=["limit"],
                ),
            ),
            types.FunctionDeclaration(
                name="room_remove_member",
                description="Thu hồi quyền truy cập phòng của thành viên",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "user_ids": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.STRING),
                            description="Danh sách user ID cần xóa khỏi phòng",
                        )
                    },
                    required=["user_ids"],
                ),
            ),
            types.FunctionDeclaration(
                name="room_allow",
                description="Cho phép thành viên vào phòng",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "user_ids": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.STRING),
                            description="Danh sách user ID cần cho phép",
                        )
                    },
                    required=["user_ids"],
                ),
            ),
            types.FunctionDeclaration(
                name="room_invite",
                description="Mời thành viên vào phòng và gửi link invite qua DM",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "user_ids": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.STRING),
                            description="Danh sách user ID cần mời",
                        )
                    },
                    required=["user_ids"],
                ),
            ),
        ]
    )
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
            # elif tool_name == "get_weather":
            #     city = tool_args.get("city", "")
            #     return json.dumps(
            #         {
            #             "city": city,
            #             "temperature": "25°C",
            #             "condition": "Partly Cloudy",
            #             "humidity": "65%",
            #             "note": "Mock data. Integrate a real weather API for production.",
            #         }
            #     )
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
                print(members)
                return await room.invite(members)

            case _:
                return f"Unknown function: {tool_name}"

        return "Không tìm thấy tool thích hợp: {tool_name}"

    except Exception:
        traceback.print_exc()
        return f"Có lỗi xảy ra khi thực hiện ({tool_name})"


async def generate_response(
    discord_message: discord.Message,
    user_message: str,
    history: list[dict],
    user_facts: list[str],
    user_id: int,
    username: str = "User",
    model_type: str = "COMPLEX",
) -> str:
    """Generate a response using async Gemini client with tool calling."""

    facts_text = (
        "\n".join(
            f"[{f.category}] {f.key} = {f.value} (confidence: {f.confidence})"
            for f in user_facts
        )
        if user_facts
        else "None stored yet."
    )
    system_prompt = f"""You are a helpful, friendly Discord bot assistant to help user learning and get more knowledge.
You have memory of this user and can use tools when needed.

User: {username} (ID: {user_id})

Facts you know about this user:
{facts_text}

## Response style:
- Default language is Vietnamese. Answer in Vietnamese except there are request to answer in other language
- If they ask you to match their tone—whatever they call you, call them right back. Else maintain a friendly tone, no need to be formal
- Be honest when you don't know something
- Keep responses under 2000 characters to fit Discord limits
- No swear and example any swear word
- Absolutely do not provide any internal information(what kind of model you are or your background, how the bot works, JSON, etc.) that can lead to security vulnerabilities. If anyone asks, just say you're a Betterme Discord bot for academic support.
- No yapping
- Avoid using complex mathematical symbols (like LaTeX). Use plain text and Discord-compatible Markdown instead:
    Plain text and standard keyboard symbols (e.g., ^ for exponents, * for multiplication).
    Unicode symbols for special characters (e.g., √, π, ±, Σ).
    Code blocks (using triple backticks ```) for complex formulas to keep them readable on Discord."
- Easy-to-understand explanation.

## Thinking Guidelines:
- Simple questions (greetings, basic facts, casual chat) → reply directly, no need to overthink
- Explanations, comparisons, simple code → think moderately
- Math problems, complex debugging, multi-step logic, proofs → think carefully and thoroughly before answering

## Tools use guidelines:
- Only use tools when truly necessary (data lookup, executing specific actions). For general questions, respond directly without calling any tools.
- If user use tools, do not care about chat history, just execute the tool and return the result without extra commentary
- Use the search_files tool when users ask about their uploaded documents
"""

    # Build message history for Gemini
    gemini_contents = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_contents.append(
            types.Content(role=role, parts=[types.Part(text=msg["content"])])
        )

    gemini_contents.append(
        types.Content(role="user", parts=[types.Part(text=user_message)])
    )

    # Select model based on routing
    selected_model = (
        env.GEMINI_LITE_MODEL if model_type == "SIMPLE" else env.GEMINI_MODEL
    )
    print(
        "Answer with model:",
        selected_model,
        ". Context: ",
        user_message,
        ". User name: ",
        username,
        ". Fact:",
        facts_text,
    )

    # Async client + agentic tool loop
    response = await aclient.models.generate_content(
        model=selected_model,
        contents=gemini_contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            tools=TOOLS,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="AUTO")
            ),
            safety_settings=SAFETY_SETTINGS,
            temperature=0.7,
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
    return "[TOOLS USE]:" + return_text
