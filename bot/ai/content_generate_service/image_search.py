"""
File selector service - analyze user message and select relevant files.
Uses Cloudflare AI with JSON structured output.
"""

import aiohttp
from pydantic import BaseModel

from core.env import env

# ─────────────────────────────────────────────
# Schema
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are a file selector assistant for a study support bot.

Your job: analyze the user's recent questions and a list of available files, then decide which files are needed to answer the user.

## Input format
You will receive:
- The 3 most recent user questions (for context)
- A list of available files, each with:
  - id: unique record identifier
  - summary: brief overview of the file content
  - detail: detailed description of the file content
  - subject: subject/topic area
  - tags: list of relevant keywords
  - has_diagram: whether the file contains diagrams/charts
  - has_table: whether the file contains tables

## Your task
Select only the files that are **directly relevant** to answer the user's latest question (considering context from earlier questions).

## Decision rules for `should_get_original_image`
Set `should_get_original_image` to `true` if ANY of these apply:
- The user explicitly asks to "see", "show", "look at", or "view" a diagram/chart/image
- The user asks about a specific diagram, figure, or visual element
- The file has `has_diagram: true` AND the question requires understanding a visual structure (e.g., circuit, process flow, anatomy, graph)
- The file has `has_table: true` AND the user needs to read exact values from the table

Set `should_get_original_image` to `false` if:
- The user only needs conceptual explanation (text is sufficient)
- The question is about definitions, theory, or steps that can be described in text
- The file content can be conveyed through the extracted text alone

## Output
Respond ONLY with a valid JSON array. No explanation, no markdown, no extra text.
Format: [{"id": <record_id>, "should_get_original_image": <bool>}, ...]

If no files are relevant, return an empty array: []"""


# ─────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────


class SelectedFile(BaseModel):
    """Model for a single selected file."""

    id: str
    should_get_original_image: bool


class SelectedFiles(BaseModel):
    """Model for the AI response containing selected files."""

    files: list[SelectedFile]


# ─────────────────────────────────────────────
# API CALL
# ─────────────────────────────────────────────


async def select_files(user_msg: str) -> SelectedFiles:
    """
    Call Cloudflare AI to select relevant files based on user message.
    Returns SelectedFiles model with list of selected files.
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
            "temperature": 0.1,
            "reasoning_effort": "low",
            "max_completion_tokens": 1500,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "selected_files",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "files": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "should_get_original_image": {
                                            "type": "boolean"
                                        },
                                    },
                                    "required": ["id", "should_get_original_image"],
                                },
                            }
                        },
                        "required": ["files"],
                    },
                },
            },
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
                content = message.get("content") or "{}"

                return SelectedFiles.model_validate_json(content)

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Cloudflare API error: {e}")
