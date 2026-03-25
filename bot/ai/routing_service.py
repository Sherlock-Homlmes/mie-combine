"""
Router service - classify message complexity and purpose.
Uses Cloudflare AI with Pydantic structured output parsing.
"""

import json
import re
from enum import Enum
from typing import Optional

import aiohttp
from pydantic import BaseModel, ValidationError

from core.env import env

# ─────────────────────────────────────────────
# Schema
# ─────────────────────────────────────────────


class Complexity(str, Enum):
    SIMPLE = "SIMPLE"
    COMPLEX = "COMPLEX"


class Purpose(str, Enum):
    FUNC_CALL = "FUNC_CALL"
    GOOGLE_SEARCH = "GOOGLE_SEARCH"
    SEARCH_IMAGES = "SEARCH_IMAGES"
    NORMAL = "NORMAL"


class RoutingResult(BaseModel):
    complexity: Complexity
    purpose: Purpose

    class Config:
        use_enum_values = True


# ─────────────────────────────────────────────
# Prompt builder
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """Bạn là một bộ định tuyến tin nhắn (Message Router) cho hệ thống trợ lý phòng học tại trường đại học. Người dùng là sinh viên và giảng viên.
Nhiệm vụ: Đọc tin nhắn và trả về JSON với 2 trường sau. KHÔNG giải thích, KHÔNG thêm text nào khác ngoài JSON.
## 1. `complexity`
- "SIMPLE": Chào hỏi, tán gẫu, nói nhảm/vô nghĩa, dịch thuật nhanh, câu hỏi thường thức đơn giản.
- "COMPLEX": Hỏi bài, giải toán, viết văn, giải thích kiến thức chuyên sâu.
## 2. `purpose`
Chọn MỘT giá trị, ưu tiên theo thứ tự từ cao xuống thấp nếu conflict:
1. "FUNC_CALL"     → Điều khiển thiết bị/phòng học vật lý: mở/khóa/quản lý room, bật/tắt đèn/máy chiếu, hỏi thời gian hiện tại (giờ là mấy giờ, hôm nay ngày mấy). HOẶC xem thống kê học tập: thời gian học, bảng xếp hạng, leaderboard, ranking, top học, ai học nhiều nhất. KHÔNG áp dụng cho câu ra lệnh thông thường về hành vi, thái độ hay lời nói.
2. "SEARCH_IMAGES" → Người dùng đề cập đến bài tập, câu hỏi, đề, ảnh hoặc file cụ thể nhưng KHÔNG có nội dung đó trong context. Dấu hiệu: "bài này", "câu này", "ảnh tao gửi", "cái đó", "giải câu 6", "giúp tao bài này", "làm đề này" mà không có attachment hay nội dung bài tập đi kèm trong context.
3. "GOOGLE_SEARCH" → Cần tra cứu internet: thời tiết, địa điểm, quán ăn, sự kiện,...
4. "NORMAL"        → Không cần tool nào, trả lời từ kiến thức có sẵn
## Quy tắc (STRICT)
- Nếu conflict → chọn purpose có độ ưu tiên cao nhất
- Nếu không chắc complexity → chọn "SIMPLE"
- Nếu không chắc purpose → chọn "NORMAL"
## Output format (STRICT)
{"complexity": "SIMPLE" | "COMPLEX", "purpose": "FUNC_CALL" | "GOOGLE_SEARCH" | "SEARCH_IMAGES" | "NORMAL"}
## Ví dụ
{"input": "mở cửa treo biển thả chó"} → {"complexity": "SIMPLE", "purpose": "FUNC_CALL"}
{"input": "mở phòng học 101"} → {"complexity": "SIMPLE", "purpose": "FUNC_CALL"}
{"input": "thời tiết hà nội hôm nay"} → {"complexity": "SIMPLE", "purpose": "GOOGLE_SEARCH"}
{"input": "giải giúp tao bài trong ảnh"} → {"complexity": "COMPLEX", "purpose": "SEARCH_IMAGES"}
{"input": "2+2 bằng mấy"} → {"complexity": "SIMPLE", "purpose": "NORMAL"}
{"input": "tìm quán ăn rồi mở phòng học"} → {"complexity": "SIMPLE", "purpose": "FUNC_CALL"}
{"input": "giải thích định lý Pythagoras"} → {"complexity": "COMPLEX", "purpose": "NORMAL"}
{"input": "xưng hô cẩn thận vào"} → {"complexity": "SIMPLE", "purpose": "NORMAL"}
{"input": "nói lại đi"} → {"complexity": "SIMPLE", "purpose": "NORMAL"}
{"input": "im đi"} → {"complexity": "SIMPLE", "purpose": "NORMAL"}
{"input": "xem thời gian học"} → {"complexity": "SIMPLE", "purpose": "FUNC_CALL"}
{"input": "tháng này tao học bao nhiêu giờ"} → {"complexity": "SIMPLE", "purpose": "FUNC_CALL"}
{"input": "ai học nhiều nhất tuần này"} → {"complexity": "SIMPLE", "purpose": "FUNC_CALL"}
{"input": "xem leaderboard"} → {"complexity": "SIMPLE", "purpose": "FUNC_CALL"}
{"input": "top học hôm nay"} → {"complexity": "SIMPLE", "purpose": "FUNC_CALL"}"""


def build_user_message(
    conversation_text: str,
    document_summaries: Optional[str] = None,
    history: Optional[list[dict]] = None,
) -> str:
    """Build user message, optionally inject document summaries and chat history."""
    msg = ""

    # Inject last 3 user messages from history
    if history:
        user_msgs = [
            m["content"]
            for m in history
            if m.get("role") == "user" and m.get("content")
        ][-3:]

        if user_msgs:
            msg += "[Lịch sử hội thoại gần đây]\n"
            msg += "\n".join(f"user: {m}" for m in user_msgs)
            msg += "\n\n"

    msg += f"[Tin nhắn hiện tại]\nuser: {conversation_text}"

    if len(document_summaries):
        msg += f"""

---
Tóm tắt tài liệu/ảnh người dùng đã gửi gần đây (dùng để quyết định có cần SEARCH_IMAGES không):
{json.dumps(document_summaries, ensure_ascii=False, indent=2)}"""

    return msg


def parse_router_result(raw: str) -> RoutingResult:
    """
    Parse raw model output → RouterResult.
    Handles: clean JSON, JSON wrapped in markdown fences, JSON buried in text.
    Raises ValueError if parsing fails.
    """
    text = raw.strip()

    # Strip markdown fences if present: ```json ... ``` or ``` ... ```
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence_match:
        text = fence_match.group(1).strip()

    # Try to extract JSON object if there's surrounding text
    json_match = re.search(r"\{[^{}]+\}", text)
    if json_match:
        text = json_match.group(0)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return raw

    try:
        return RoutingResult(**data)
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Invalid router result schema: {data} → {e}")


# ─────────────────────────────────────────────
# API caller
# ─────────────────────────────────────────────


async def route_message(
    conversation_text: str,
    document_summaries: Optional[str] = None,
    history: Optional[list[dict]] = None,
) -> RoutingResult:
    """
    Call Cloudflare AI router model and return structured RouterResult.
    Falls back to COMPLEX/NORMAL on any error.
    """
    user_msg = build_user_message(conversation_text, document_summaries, history)

    async with aiohttp.ClientSession() as session:
        url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{env.CLOUDFLARE_ACCOUNT_ID}/ai/run/{env.CLOUDFLARE_ROUTING_MODEL}"
        )
        headers = {"Authorization": f"Bearer {env.CLOUDFLARE_API_KEY}"}
        payload = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            "max_tokens": 60,  # JSON output ngắn, không cần nhiều
            "temperature": 0.1,  # Deterministic
            "json_schema": RoutingResult.model_json_schema(),
        }

        try:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                data = await response.json()
                if response.status != 200:
                    raise ValueError(f"HTTP {response.status}: {data}")

                raw_text = data["result"].get("response", "").strip()
                return parse_router_result(raw_text)

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Cloudflare API error: {e}")
