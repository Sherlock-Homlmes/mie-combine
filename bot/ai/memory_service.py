"""
Mem0-inspired memory service backed by MongoDB (via Beanie).
Extracts and stores user facts using Gemini async client.
"""

import json
from datetime import datetime
from loguru import logger

from models import UserFact
from utils.ai_coversation import aclient, ai_lite_model


EXTRACT_FACTS_PROMPT = """You are a memory extraction assistant. Given a conversation, extract important facts about the USER (not the assistant).

Facts to extract:
- Personal info (name, age, location, job, etc.)
- Preferences and interests
- Important context they've shared
- Goals or problems they mentioned

Return a JSON array of fact strings. Each fact should be concise and factual.
Example: ["User's name is Alex", "User is a software engineer", "User likes Python"]

If no new facts, return: []

Conversation:
{conversation}

Existing facts (don't duplicate):
{existing_facts}

Return ONLY valid JSON array, nothing else."""


async def extract_and_store_facts(
    user_id: str, guild_id: str, conversation: list[dict]
) -> list[str]:
    """Extract facts from conversation and store in MongoDB."""
    try:
        user_fact = await UserFact.find_one(UserFact.user_id == user_id)
        existing = user_fact.raw_memories if user_fact else []

        conv_text = "\n".join(
            [f"{m['role'].upper()}: {m['content']}" for m in conversation[-6:]]
        )

        response = await aclient.models.generate_content(
            model=ai_lite_model,
            contents=EXTRACT_FACTS_PROMPT.format(
                conversation=conv_text, existing_facts=json.dumps(existing)
            ),
        )

        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        new_facts: list[str] = json.loads(raw)
        if not new_facts:
            return existing

        merged = list(set(existing + new_facts))

        if user_fact:
            user_fact.raw_memories = merged
            user_fact.updated_at = datetime.utcnow()
            await user_fact.save()
        else:
            user_fact = UserFact(
                user_id=user_id,
                guild_id=guild_id,
                raw_memories=merged,
                facts=[
                    {"text": f, "created_at": datetime.utcnow().isoformat()}
                    for f in new_facts
                ],
            )
            await user_fact.insert()

        logger.info(f"Stored {len(new_facts)} new facts for user {user_id}")
        return merged

    except Exception as e:
        logger.error(f"Failed to extract facts for user {user_id}: {e}")
        return []


async def get_user_facts(user_id: str) -> list[str]:
    user_fact = await UserFact.find_one(UserFact.user_id == user_id)
    if not user_fact:
        return []
    return user_fact.raw_memories
