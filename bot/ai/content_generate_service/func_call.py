"""
Function calling service - analyze user message and call appropriate room tools.
Uses Cloudflare AI with function calling capability.
"""

import json

import aiohttp

from core.env import env

# ─────────────────────────────────────────────
# Schema
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """Bạn là trợ lý quản lý phòng. Phân tích yêu cầu người dùng và gọi đúng tool tương ứng.
Nếu không xác định được hành động cụ thể, gọi tool mày thấy giống nhất. Khó quá mới trả về list rỗng"""

ROOM_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Lấy thời gian hiện tại. Thay thế: bây giờ là mấy giờ, hiện tại là mấy giờ, giờ hiện tại,...",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "room_public",
            "description": "Cho phép mọi người vào phòng. Thay thế: mở phòng, mở cửa, cho mọi người vào,...",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "room_private",
            "description": "Không cho phép mọi người vào phòng. Thay thế: khóa phòng, đóng cửa, không cho mọi người vào,...",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "room_show",
            "description": "Phòng đang bị ẩn. Hiển thị phòng cho mọi người thấy. Thay thế: hiển thị phòng, cho mọi người thấy phòng,...",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "room_hide",
            "description": "Ẩn phòng không cho mọi người thấy. Thay thế: ẩn phòng, giấu phòng, đừng cho mọi người thấy phòng,...",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "room_mute",
            "description": "Tắt âm phòng. Thay thế: tắt tiếng phòng, im lặng phòng, đừng cho tiếng phòng, cho bọn này im dùm,...",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "room_unmute",
            "description": "Bật âm thanh phòng. Thay thế: bật tiếng phòng, cho phòng nói chuyện lại,...",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "room_rename",
            "description": "Đổi tên phòng. Thay thế: treo biển, đổi tên thành, đặt tên là,...",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Tên mới của phòng",
                    }
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "room_limit",
            "description": "Đặt giới hạn số người trong phòng",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số người tối đa",
                    }
                },
                "required": ["limit"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "room_remove_member",
            "description": "Thu hồi quyền truy cập phòng của thành viên. Thay thế: đá, kick, đuổi, cấm,...",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Danh sách user ID cần xóa khỏi phòng",
                    }
                },
                "required": ["user_ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "room_allow",
            "description": "Cho phép thành viên vào phòng. Thay thế: cho vào, bỏ cấm, cho phép,...",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Danh sách user ID cần cho phép",
                    }
                },
                "required": ["user_ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "room_invite",
            "description": "Mời thành viên vào phòng và gửi link invite qua DM. Thay thế: mời, gửi link, gửi thiệp, cho vào rồi gửi link,...",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Danh sách user ID cần mời",
                    }
                },
                "required": ["user_ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_study_time",
            "description": "Xem thống kê thời gian học của bản thân. Thay thế: thời gian học, bao nhiêu giờ học, check giờ học, xem học bao lâu,...",
            "parameters": {
                "type": "object",
                "properties": {
                    "time_range": {
                        "type": "string",
                        "enum": ["Tháng này", "Tuần này", "Hôm nay"],
                        "description": "Khoảng thời gian cần xem thống kê",
                    }
                },
                "required": ["time_range"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_leaderboard",
            "description": "Xem bảng xếp hạng thời gian học của server. Thay thế: xếp hạng, top học, ai học nhiều nhất, leaderboard, ranking,...",
            "parameters": {
                "type": "object",
                "properties": {
                    "time_range": {
                        "type": "string",
                        "enum": ["Tất cả", "Tháng này", "Tuần này", "Hôm nay"],
                        "description": "Khoảng thời gian của bảng xếp hạng",
                    }
                },
                "required": ["time_range"],
            },
        },
    },
]


# ─────────────────────────────────────────────
# API CALL
# ─────────────────────────────────────────────


async def call_function(user_msg: str) -> list[dict]:
    """
    Call Cloudflare AI with function calling to analyze user message.
    Returns list of tool calls with their arguments, empty list if no tool matched.
    """
    async with aiohttp.ClientSession() as session:
        url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{env.CLOUDFLARE_ACCOUNT_ID}/ai/run/{env.CLOUDFLARE_FUNCTION_MODEL}"
        )
        headers = {"Authorization": f"Bearer {env.CLOUDFLARE_API_KEY}"}
        payload = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            "tools": ROOM_TOOLS,
            "tool_choice": "auto",
            "temperature": 1,
            "reasoning_effort": "low",
            "max_completion_tokens": 1500,
        }

        try:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as response:
                data = await response.json()
                if response.status != 200:
                    raise ValueError(f"HTTP {response.status}: {data}")

                message = data["result"]["choices"][0]["message"]
                tool_calls = message.get("tool_calls") or []

                results = []
                for tc in tool_calls:
                    fn = tc["function"]
                    results.append(
                        {
                            "tool": fn["name"],
                            "args": json.loads(fn["arguments"])
                            if fn["arguments"]
                            else {},
                        }
                    )

                return results

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Cloudflare API error: {e}")
