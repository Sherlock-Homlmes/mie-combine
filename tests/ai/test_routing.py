"""
Router service - classify message complexity and purpose.
Uses Cloudflare AI with Pydantic structured output parsing.
"""

import asyncio
import json
import re
import time
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

SYSTEM_PROMPT = """Mày là một bộ định tuyến tin nhắn (Message Router) cho hệ thống trợ lý phòng học thông minh.

Đọc tin nhắn người dùng và trả về JSON với 2 trường sau. KHÔNG giải thích, KHÔNG thêm text nào khác ngoài JSON.

## 1. `complexity`
- "SIMPLE": Chào hỏi, tán gẫu, nói nhảm/vô nghĩa, dịch thuật nhanh, câu hỏi thường thức đơn giản.
- "COMPLEX": Hỏi bài, giải toán, viết văn, giải thích kiến thức chuyên sâu.

## 2. `purpose`
Chọn MỘT giá trị, ưu tiên theo thứ tự từ cao xuống thấp nếu conflict:

1. "FUNC_CALL"     → Điều khiển phòng học: mở/khóa/quản lý room, thực hiện lệnh server
2. "GOOGLE_SEARCH" → Cần tra cứu internet: thời tiết, địa điểm, quán ăn, sự kiện,...
3. "SEARCH_IMAGES" → Người dùng đề cập đến ảnh/file đã gửi trước nhưng không thấy trong context. Dấu hiệu: "bài này", "ảnh tao gửi", "cái đó" mà không có attachment
4. "NORMAL"        → Không cần tool nào, trả lời từ kiến thức có sẵn

## Quy tắc (STRICT)
- Nếu conflict → chọn purpose có độ ưu tiên cao nhất
- Nếu không chắc complexity → chọn "COMPLEX"
- Nếu không chắc purpose → chọn "NORMAL"

## Output format (STRICT)
{"complexity": "SIMPLE" | "COMPLEX", "purpose": "FUNC_CALL" | "GOOGLE_SEARCH" | "SEARCH_IMAGES" | "NORMAL"}

## Ví dụ
{"input": "mở phòng học 101"} → {"complexity": "SIMPLE", "purpose": "FUNC_CALL"}
{"input": "thời tiết hà nội hôm nay"} → {"complexity": "SIMPLE", "purpose": "GOOGLE_SEARCH"}
{"input": "giải giúp tao bài trong ảnh"} → {"complexity": "COMPLEX", "purpose": "SEARCH_IMAGES"}
{"input": "2+2 bằng mấy"} → {"complexity": "SIMPLE", "purpose": "NORMAL"}
{"input": "tìm quán ăn rồi mở phòng học"} → {"complexity": "SIMPLE", "purpose": "FUNC_CALL"}
{"input": "giải thích định lý Pythagoras"} → {"complexity": "COMPLEX", "purpose": "NORMAL"}"""


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

    if document_summaries and document_summaries.strip():
        msg += f"""

---
Tóm tắt tài liệu/ảnh người dùng đã gửi gần đây (dùng để quyết định có cần SEARCH_IMAGES không):
{document_summaries.strip()}"""

    return msg


# ─────────────────────────────────────────────
# Parser
# ─────────────────────────────────────────────


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
    except json.JSONDecodeError as e:
        raise ValueError(f"Cannot parse JSON from model output: '{raw}' → {e}")

    try:
        return RoutingResult(**data)
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Invalid router result schema: {data} → {e}")


# ─────────────────────────────────────────────
# API caller
# ─────────────────────────────────────────────


async def call_router(
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
            # "max_completion_tokens": 1024,
            "reasoning_effort": None,
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
                print(data)
                if response.status != 200:
                    # Cloudflare trả về lỗi "JSON Mode couldn't be met" ở đây
                    raise ValueError(f"HTTP {response.status}: {data}")

                raw_text = data["result"].get("response", "").strip()
                return parse_router_result(raw_text)

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Cloudflare API error: {e}")


# ─────────────────────────────────────────────
# Test
# ─────────────────────────────────────────────


async def test_router():
    test_cases = [
        # (input, doc_summaries, history, expected_complexity, expected_purpose)
        ("mở phòng học 101", None, [], "SIMPLE", "FUNC_CALL"),
        ("thời tiết hà nội hôm nay", None, [], "SIMPLE", "GOOGLE_SEARCH"),
        ("giải giúp tao bài trong ảnh", None, [], "COMPLEX", "SEARCH_IMAGES"),
        ("2+2 bằng mấy", None, [], "SIMPLE", "NORMAL"),
        ("tìm quán ăn rồi mở phòng học", None, [], "SIMPLE", "FUNC_CALL"),
        ("giải thích định lý Pythagoras", None, [], "COMPLEX", "NORMAL"),
        ("xin chào", None, [], "SIMPLE", "NORMAL"),
        # Case có document summaries
        (
            "giải bài này cho tao",
            "[img_001.jpg] Bài tập hình học: tính diện tích tam giác ABC",
            [],
            "COMPLEX",
            "SEARCH_IMAGES",
        ),
    ]
    long_context_test_cases = [
        # --- Long context cases ---
        (
            "cái đó sai rồi",
            None,
            [
                {"role": "user", "content": "giải pt bậc 2: x^2 - 5x + 6 = 0"},
                {"role": "assistant", "content": "x = 2 hoặc x = 3"},
                {"role": "user", "content": "ừ nhưng tao thấy kết quả lạ"},
            ],
            "COMPLEX",
            "NORMAL",
        ),
        (
            "mở phòng đi",
            None,
            [
                {"role": "user", "content": "hôm nay học môn gì vậy"},
                {"role": "user", "content": "ừ thôi học toán đi"},
                {"role": "user", "content": "phòng nào còn trống không"},
            ],
            "SIMPLE",
            "FUNC_CALL",
        ),
        (
            "câu tiếp theo làm sao",
            None,
            [
                {"role": "user", "content": "giải bài tập hóa này cho tao"},
                {"role": "assistant", "content": "câu a: ..."},
                {"role": "user", "content": "oke câu a hiểu rồi"},
            ],
            "COMPLEX",
            "NORMAL",
        ),
        (
            "cái ảnh lúc nãy ý",
            "[img_004.jpg] Đề bài hình học không gian",
            [
                {"role": "user", "content": "tao vừa gửi ảnh rồi đó"},
                {"role": "assistant", "content": "tao chưa thấy ảnh nào"},
                {"role": "user", "content": "ảnh tao chụp đề bài ấy"},
            ],
            "COMPLEX",
            "SEARCH_IMAGES",
        ),
        (
            "thôi kệ, tìm quán ăn gần đây đi",
            None,
            [
                {"role": "user", "content": "giải thích recursion cho tao"},
                {"role": "assistant", "content": "recursion là..."},
                {"role": "user", "content": "ừ hiểu rồi"},
            ],
            "SIMPLE",
            "GOOGLE_SEARCH",
        ),
        (
            "câu đó",
            None,
            [
                {"role": "user", "content": "dịch 'good morning' ra tiếng việt"},
                {"role": "assistant", "content": "chào buổi sáng"},
                {"role": "user", "content": "còn 'good night' thì sao"},
            ],
            "SIMPLE",
            "NORMAL",  # refer đến dịch thuật → SIMPLE
        ),
    ]

    # ── Hard cases ──────────────────────────────────────────────────────────
    # Những case dễ bị nhầm lẫn giữa các category
    hard_test_cases = [
        # --- FUNC_CALL vs GOOGLE_SEARCH ---
        # Nghe như tìm kiếm nhưng thực ra là lệnh điều khiển
        ("cho tao vào phòng gần nhất còn trống", None, [], "SIMPLE", "FUNC_CALL"),
        # Đề cập địa điểm nhưng mục đích là mở phòng
        ("mở phòng học ở tầng 2 cho tao", None, [], "SIMPLE", "FUNC_CALL"),
        # Conflict rõ → ưu tiên FUNC_CALL
        ("tìm quán cafe gần đây rồi khóa phòng 302", None, [], "SIMPLE", "FUNC_CALL"),
        # --- GOOGLE_SEARCH vs NORMAL ---
        # Câu hỏi tưởng như AI biết nhưng cần realtime
        ("hôm nay trời hà nội có mưa không", None, [], "SIMPLE", "GOOGLE_SEARCH"),
        # Từ "gần đây" → cần location search
        ("quán trà sữa ngon gần đây", None, [], "SIMPLE", "GOOGLE_SEARCH"),
        # Tưởng NORMAL nhưng cần current data
        ("giá vàng hôm nay bao nhiêu", None, [], "SIMPLE", "GOOGLE_SEARCH"),
        # Lịch sự kiện → cần search
        ("lịch thi đấu V-League tuần này", None, [], "SIMPLE", "GOOGLE_SEARCH"),
        # --- SEARCH_IMAGES vs COMPLEX/NORMAL ---
        # Không có ảnh đính kèm, dùng đại từ mơ hồ
        ("cái này sai ở đâu vậy", None, [], "COMPLEX", "SEARCH_IMAGES"),
        ("bài tao vừa gửi làm được chưa", None, [], "SIMPLE", "SEARCH_IMAGES"),
        # Có doc summary → phải SEARCH_IMAGES dù câu hỏi ngắn
        (
            "đúng không",
            "[img_002.jpg] Bài giải phương trình bậc 2 của học sinh",
            [],
            "COMPLEX",
            "SEARCH_IMAGES",
        ),
        # Không có doc summary, không có "ảnh" → NORMAL
        ("bài toán này giải thế nào", None, [], "COMPLEX", "NORMAL"),
        # --- SIMPLE vs COMPLEX (ranh giới mờ) ---
        # Dịch thuật → SIMPLE dù câu dài
        (
            "dịch giúp tao đoạn này sang tiếng anh: 'học sinh cần nộp bài trước 5 giờ chiều'",
            None,
            [],
            "SIMPLE",
            "NORMAL",
        ),
        # Tưởng chào hỏi nhưng là câu hỏi thực sự
        ("ê mày giải thích recursion cho tao hiểu với", None, [], "COMPLEX", "NORMAL"),
        # Toán đơn giản → SIMPLE
        ("25 nhân 48 bằng bao nhiêu", None, [], "SIMPLE", "NORMAL"),
        # Toán có lý thuyết → COMPLEX
        (
            "tại sao 0.1 + 0.2 không bằng 0.3 trong python",
            None,
            [],
            "COMPLEX",
            "NORMAL",
        ),
        # --- Tiếng Việt teen/slang dễ bị misclassify ---
        ("ê mở room đi mày", None, [], "SIMPLE", "FUNC_CALL"),
        ("phòng bị khóa rồi kìa, mở ra đi", None, [], "SIMPLE", "FUNC_CALL"),
        ("tìm chỗ học ielts ở hà nội uy tín", None, [], "SIMPLE", "GOOGLE_SEARCH"),
        (
            "mày biết quán bún bò nào ngon ở đống đa không",
            None,
            [],
            "SIMPLE",
            "GOOGLE_SEARCH",
        ),
        # --- Câu cụt/thiếu ngữ cảnh ---
        # Quá ngắn, không có attachment → không thể biết "bài" là gì → SEARCH_IMAGES
        ("bài này", None, [], "COMPLEX", "SEARCH_IMAGES"),
        # Nhưng nếu có doc summary → confirm SEARCH_IMAGES
        (
            "bài này",
            "[img_003.jpg] Đề văn nghị luận xã hội về môi trường",
            [],
            "COMPLEX",
            "SEARCH_IMAGES",
        ),
        # --- Mixed language (Việt + Anh) ---
        ("lock the room đi mày", None, [], "SIMPLE", "FUNC_CALL"),
        ("search giúp tao weather hà nội", None, [], "SIMPLE", "GOOGLE_SEARCH"),
        ("explain recursion bằng tiếng việt cho tao", None, [], "COMPLEX", "NORMAL"),
    ]

    async def run_suite(suite: list, label: str, index_offset: int = 0):
        passed = 0
        failed = []
        start = time.time()
        for i, (inp, docs, his, exp_complexity, exp_purpose) in enumerate(suite, 1):
            idx = i + index_offset
            t0 = time.time()
            try:
                result = await call_router(inp, docs, his)
                duration = time.time() - t0
                ok = (
                    result.complexity == exp_complexity
                    and result.purpose == exp_purpose
                )
                status = "✓ PASS" if ok else "✗ FAIL"
                if ok:
                    passed += 1
                else:
                    failed.append(
                        (idx, inp, docs, his, exp_complexity, exp_purpose, result)
                    )
                print(f"\nTest {idx}: {status} ({duration:.2f}s)")
                print(f"  Input    : {inp}")
                if docs:
                    print(f"  Docs     : {docs[:70]}...")
                print(
                    f"  Expected : complexity={exp_complexity}, purpose={exp_purpose}"
                )
                print(
                    f"  Got      : complexity={result.complexity}, purpose={result.purpose}"
                )
            except Exception as e:
                duration = time.time() - t0
                print(f"\nTest {idx}: ✗ ERROR ({duration:.2f}s)")
                print(f"  Input : {inp}")
                print(f"  Error : {e}")
                failed.append((idx, inp, exp_complexity, exp_purpose, None))
        elapsed = time.time() - start
        return passed, failed, elapsed

    print("=" * 70)
    print("TESTING ROUTER SERVICE")
    print(f"Model: {env.CLOUDFLARE_ROUTING_MODEL}")
    print("=" * 70)

    print("\n▶ BASIC CASES")
    print("-" * 70)
    b_passed, b_failed, b_time = await run_suite(test_cases, "BASIC")

    print("\n\n▶ LONG CONTEXT CASES")
    print("-" * 70)
    l_passed, l_failed, l_time = await run_suite(
        long_context_test_cases, "LONG_CONTEXT", index_offset=len(test_cases)
    )

    print("\n\n▶ HARD CASES")
    print("-" * 70)
    h_passed, h_failed, h_time = await run_suite(
        hard_test_cases, "HARD", index_offset=len(test_cases)
    )

    total_passed = b_passed + h_passed + l_passed
    all_failed = b_failed + h_failed + l_failed
    total = len(test_cases) + len(hard_test_cases) + len(long_context_test_cases)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print(f"  Basic : {b_passed}/{len(test_cases)} passed ({b_time:.2f}s)")
    print(
        f"  Long context  : {l_passed}/{len(long_context_test_cases)} passed ({l_time:.2f}s)"
    )
    print(f"  Hard  : {h_passed}/{len(hard_test_cases)} passed ({h_time:.2f}s)")
    print(f"  Total : {total_passed}/{total} passed ({b_time + h_time + l_time:.2f}s)")

    if all_failed:
        print(f"\nFAILED ({len(all_failed)}):")
        for item in all_failed:
            idx, inp, docs, his, ec, ep, got = item
            got_str = f"({got.complexity}, {got.purpose})" if got else "ERROR"
            print(
                f"  [{idx}] {docs} | {his} | '{inp[:55]}' → expected ({ec}, {ep}), got {got_str}"
            )
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_router())
