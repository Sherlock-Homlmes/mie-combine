"""
Mem0-inspired memory service backed by MongoDB (via Beanie).
Extracts and stores user facts using Gemini async client.
"""

from enum import Enum
from typing import List

from google.genai import types
from pydantic import BaseModel, Field, TypeAdapter

from core.env import env
from models import FactSourceEnum, UserFactCategoryEnum, UserFactHistory, UserFacts
from utils.ai_coversation import aclient
from utils.time_modules import Now

CONFIDENCE_UPDATE_THRESHOLD = 0.7
CONFIDENCE_FETCH_THRESHOLD = 0.4
EXTRACT_FACTS_PROMPT = """
You are a memory extraction assistant for a Discord bot. Analyze the conversation and extract important facts about the USER (not the assistant).

Current known facts:
{existing_facts}

Weak signals (low-confidence, update if you find stronger evidence):
{weak_signals}

Conversation:
{conversation}

Rules:
- Only extract facts about the USER, never about the assistant
- Only cite facts. If it's not a fact, ignore it.
- For context category, confidence should be <= 0.8 since it changes frequently
- For implicit/inferred facts, confidence should be <= 0.7
- If nothing new to extract, return an empty list

For facts that match an existing one (same category + key):
- If the value is the same or similar → set match_type to "reinforcement"
- If the value contradicts or differs significantly → set match_type to "contradiction"
- If it's a brand new fact not in known facts → set match_type to "new"
"""


class ExtractdFactMatchTypeEnum(str, Enum):
    NEW = "new"
    REINFORCEMENT = "reinforcement"
    CONTRADICTION = "contradiction"


class ExtractedFact(BaseModel):
    category: UserFactCategoryEnum = Field(
        description="Category of the memory to store about the user. Choose the most specific one that fits:\n"
        "- preference: Things the user likes, dislikes, or prefers (e.g. favorite language, preferred response style, hates long explanations)\n"
        "- skill: Abilities or technical knowledge the user has (e.g. knows Python, fluent in English, experienced with Docker)\n"
        "- personal: Identity and background info (e.g. name, age, job, timezone, country)\n"
        "- habit: Recurring behaviors or routines (e.g. codes at night, takes breaks every hour, always uses dark mode)\n"
        "- goal: Something the user wants to achieve short or long term (e.g. learn Rust, launch app by Q3, get a job at Google)\n"
        "- knowledge: Facts or domain knowledge the user knows or has shared (e.g. understands transformers, knows how DNS works)\n"
        "- struggle: Difficulties, blockers, or frustrations the user is facing (e.g. bad at math, keeps forgetting git commands, struggles with async)\n"
        "- progress: Milestones or progress updates on a goal or project (e.g. finished chapter 3, deployed v1, passed interview round 1)\n"
        "- context: Temporary situational info that may change soon (e.g. currently busy, just woke up, in the middle of a hackathon)\n"
    )
    key: str = Field(
        description="Short, unique identifier within the category. Use snake_case. "
        "Be specific enough to avoid collision. "
        "Examples: 'preferred_language', 'current_project', 'best_friend_name', 'wake_up_time'."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score from 0.0 to 1.0. "
        "1.0 = user stated it directly and clearly. "
        "0.7-0.9 = strongly implied. "
        "0.4-0.6 = inferred, could be wrong. "
        "Below 0.4 = weak signal, consider not saving.",
    )
    match_type: ExtractdFactMatchTypeEnum = Field(
        description="If a fact matches an existing one (same category + key):"
        '- Same or similar value → mark as "reinforcement"'
        '- Different or contradicting value → mark as "contradiction"'
    )
    source: FactSourceEnum = Field(
        description="How this memory was obtained. "
        "'explicit' = user directly stated it (e.g. 'I prefer dark mode'). "
        "'implicit' = inferred from behavior or context (e.g. user always codes at night → night owl habit)."
    )
    value: str = Field(
        description="The actual value of the memory. Be concise but complete. "
        "For relationships, include context (e.g. 'An, college friend, often mentioned when talking about gaming'). "
        "For skills, include proficiency if mentioned (e.g. 'Python - advanced'). "
        "For context, note that this may be temporary."
    )


def merge_confidence(existing: float, new: float) -> float:
    high = max(existing, new)
    low = min(existing, new)
    boost = low * 0.1
    return min(1.0, high + boost)


async def upsert_facts(
    user_discord_id: int, original_message: str, new_facts: list[ExtractedFact]
):
    for fact in new_facts:
        existing = await UserFacts.find_one(
            UserFacts.user_discord_id == user_discord_id,
            UserFacts.category == fact.category,
            UserFacts.key == fact.key,
        )
        updated_at = Now().now
        new_fact_history = UserFactHistory(
            value=fact.value, original_message=original_message, timestamp=updated_at
        )

        if existing is None or fact.match_type == "new":
            # Insert mọi confidence để track weak signals
            await UserFacts(
                user_discord_id=user_discord_id,
                category=fact.category,
                key=fact.key,
                value=fact.value,
                source=fact.source,
                confidence=fact.confidence,
                history=[new_fact_history],
            ).insert()
            continue

        elif fact.match_type == "reinforcement":
            # Luôn update vì confidence chỉ tăng, không cần threshold
            existing.confidence = merge_confidence(existing.confidence, fact.confidence)

        elif fact.match_type == "contradiction":
            should_update = (
                fact.confidence >= CONFIDENCE_UPDATE_THRESHOLD
                or fact.confidence > existing.confidence
            )
            if not should_update:
                continue

            existing.value = fact.value
            existing.source = fact.source
            existing.confidence = fact.confidence

        existing.history.append(new_fact_history)
        existing.updated_at = updated_at
        await existing.save()


async def extract_and_store_facts(
    user_discord_id: int, conversation: list[dict]
) -> list[str]:
    """Extract facts from conversation and store in MongoDB."""
    all_facts = await get_user_facts(user_discord_id)
    strong_facts = [f for f in all_facts if f.confidence >= CONFIDENCE_FETCH_THRESHOLD]
    weak_facts = [f for f in all_facts if f.confidence < CONFIDENCE_FETCH_THRESHOLD]

    conv_text = "\n".join(
        [f"{m['role'].upper()}: {m['content']}" for m in conversation]
    )

    list_schema = TypeAdapter(List[ExtractedFact]).json_schema()
    response = await aclient.models.generate_content(
        model=env.GEMINI_LITE_MODEL,
        contents=EXTRACT_FACTS_PROMPT.format(
            conversation=conv_text,
            existing_facts=strong_facts,
            weak_signals=weak_facts,
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list_schema,
        ),
    )

    extracted_facts = TypeAdapter(List[ExtractedFact]).validate_json(response.text)
    original_message = conversation[-2]["content"]
    await upsert_facts(user_discord_id, original_message, extracted_facts)

    # try:
    # except Exception as e:
    #     print(f"Failed to extract facts for user {user_discord_id}: {e}")
    #     return []


async def get_user_facts(
    user_discord_id: str, only_strong_fact: bool = False
) -> list[str]:
    query = UserFacts.find(UserFacts.user_discord_id == user_discord_id)

    if only_strong_fact:
        query = query.find(UserFacts.confidence >= CONFIDENCE_FETCH_THRESHOLD)

    return await query.to_list()
