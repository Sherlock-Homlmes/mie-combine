"""
Routing service using Cloudflare Worker AI to classify message complexity.
Returns COMPLEX for complex queries or SIMPLE for casual chat.
"""

import asyncio
import traceback

import aiohttp

from core.env import env

# Model routing constants
COMPLEX = "COMPLEX"
SIMPLE = "SIMPLE"


async def classify_message_complexity(
    message_content: str, has_attachments: bool = False
) -> str:
    """
    Classify message complexity using Cloudflare Worker AI.

    Args:
        message_content: The text content of the message
        has_attachments: Whether the message contains image attachments

    Returns:
        "COMPLEX" for complex/academic queries or messages with images
        "SIMPLE" for casual conversation or action commands
    """

    # Quick check: if message has images, always use complex model
    if has_attachments:
        return COMPLEX

    content_lower = message_content.lower().strip()

    # Quick check: if message is very short and looks like casual chat
    casual_patterns = [
        "hi",
        "hello",
        "chào",
        "hế lô",
        "hey",
        "thanks",
        "cảm ơn",
        "thank",
        "tks",
        "ok",
        "okay",
        "oke",
        "được",
        "bye",
        "tạm biệt",
        "bai",
        "đâu",
        "hả",
        "à",
        "ừ",
        "ừm",
        "😊",
        "👍",
        "❤️",
        "🎉",
    ]

    for pattern in casual_patterns:
        if content_lower == pattern or content_lower.startswith(pattern + " "):
            return SIMPLE

    # Use Cloudflare Worker AI for classification
    try:
        if not env.CLOUDFLARE_API_KEY or not env.CLOUDFLARE_ACCOUNT_ID:
            # No Cloudflare API key configured, use heuristic
            return _heuristic_classification(message_content)

        result = await _cloudflare_ai_classification(message_content)
        return result

    except Exception as e:
        print(f"Routing service error: {e}")
        traceback.print_exc()
        print("heuristic 2")
        # Fallback to heuristic classification
        return _heuristic_classification(message_content)


async def _cloudflare_ai_classification(message_content: str) -> str:
    """
    Use Cloudflare Worker AI to classify message complexity.
    """

    sys_prompt = """
Mày là một bộ định tuyến tin nhắn (Router). Hãy đọc tin nhắn của người dùng và trả về duy nhất một từ: "SIMPLE" hoặc "COMPLEX".
- Trả về "SIMPLE" nếu: Người dùng chào hỏi, tán gẫu, hoặc yêu cầu điều khiển phòng học (mở/khóa/quản lý room), thực hiện lệnh server.
- Trả về "COMPLEX" nếu: Người dùng hỏi bài tập, nhờ giải toán, nhờ viết văn, hoặc yêu cầu giải thích kiến thức chuyên sâu.
Chỉ trả về "SIMPLE" hoặc "COMPLEX", không giải thích gì thêm. Nếu không chắc thì trả về "COMPLEX".
"""

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.cloudflare.com/client/v4/accounts/{env.CLOUDFLARE_ACCOUNT_ID}/ai/run/{env.CLOUDFLARE_ROUTING_MODEL}"
            headers = {"Authorization": f"Bearer {env.CLOUDFLARE_API_KEY}"}
            payload = {
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": f'Message: "{message_content}"'},
                ],
                "max_tokens": 10,
                "temperature": 0.1,
            }

            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                print(
                    1111, url, response.status, await response.json(), message_content
                )
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("result"):
                        result_text = data["result"].get("response", "").strip().upper()
                        if "COMPLEX" in result_text:
                            return COMPLEX
                        elif "SIMPLE" in result_text:
                            return SIMPLE

                # If Cloudflare AI fails, fall back to heuristic
                return _heuristic_classification(message_content)

    except asyncio.TimeoutError:
        print("Cloudflare AI timeout, using heuristic classification")
        return _heuristic_classification(message_content)
    except Exception as e:
        print(f"Cloudflare AI error: {e}")
        return _heuristic_classification(message_content)


def _heuristic_classification(message_content: str) -> str:
    """
    Fallback heuristic classification when AI is unavailable.
    """
    content_lower = message_content.lower().strip()

    # Academic/complex indicators
    complex_keywords = [
        "giải",
        "giải thích",
        "help",
        "trợ giúp",
        "hỗ trợ",
        "làm sao",
        "làm thế nào",
        "how",
        "what",
        "why",
        "when",
        "where",
        "tại sao",
        "như thế nào",
        "ví dụ",
        "example",
        "bài tập",
        "homework",
        "exercise",
        "đề",
        "test",
        "toán",
        "math",
        "lí",
        "physic",
        "hóa",
        "chemistry",
        "code",
        "lập trình",
        "programming",
        "function",
        "algorithm",
        "phân tích",
        "analysis",
        "so sánh",
        "compare",
        "tính",
        "calculate",
        "đạo hàm",
        "tích phân",
        "công thức",
        "formula",
        "định lý",
        "theorem",
    ]

    # Check for complex keywords
    for keyword in complex_keywords:
        if keyword in content_lower:
            return COMPLEX

    # Check for question marks (indicates questions)
    if "?" in message_content:
        return COMPLEX

    # Check message length - longer messages tend to be complex
    if len(message_content) > 100:
        return COMPLEX

    # Default to SIMPLE for short, simple messages
    return SIMPLE
