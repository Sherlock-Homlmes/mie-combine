"""
Handles file upload, text extraction, chunking, and embedding pipeline.
"""

import asyncio
import json
from typing import List

import discord
from google.genai import types
from PIL import Image
from pydantic import BaseModel, Field

from core.env import env
from models import ExtractFileRecords
from utils.ai_coversation import aclient
from utils.image_handle import random_filename_from_url, save_image

CACHE_FILE_FOLDER_PATH = "assets/cache/"
TEXT_EXTENSIONS = {"txt", "md", "py", "js", "ts", "json", "csv"}
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
CHUNK_SIZE = 1500  # characters per chunk
CHUNK_OVERLAP = 200
MAX_FILE_SIZE_MB = 20
IMAGE_EXTRACT_CONFIDENCE_THRESHOLD = 0.5
IMAGE_EXTRACT_PROMPT = """
Act as a high-precision Academic OCR Assistant. Your goal is to transcribe everything from this image into a structured text format that another AI can use to solve the problems later.

### INSTRUCTIONS:
1. **Verbatim Transcription**: Extract all text exactly as written. Do not summarize or skip any words.
2. **Mathematical Expressions**: Convert ALL mathematical formulas, equations, and symbols into LaTeX format (e.g., use $x^2 + y^2 = r^2$ or $$\frac{-b \pm \sqrt{D}}{2a}$$).
3. **Diagrams & Geometry**: If there are shapes, graphs, or diagrams:
- Describe them in extreme detail (e.g., "A right-angled triangle ABC with angle B = 90 degrees, side AB = 5cm, AC = 13cm").
- For graphs, describe the axes, the type of curve, and any specific points (intercepts, peaks, etc.).
4. **Tables & Lists**: Convert any tables into clean Markdown table format. Maintain the structure of numbered or bulleted lists.
5. **Contextual Layout**: Maintain the logical order of the questions (Question 1, Question 2, etc.).
6. **No Solutions**: DO NOT solve the problems. Only extract and describe.
""".strip()


class BoundingBox(BaseModel):
    # Gemini returns [ymin, xmin, ymax, xmax]
    box_2d: List[int] = Field(
        description="The normalized coordinates [ymin, xmin, ymax, xmax] of the bounding box on a scale of 0-1000."
    )
    label: str = Field(
        description="A short, concise label for this item (e.g., 'Exercise 1', 'Geometry Diagram', 'Data Table')."
    )
    content_summary: str = Field(
        description="A detailed summary of the content within this region, optimized for semantic Vector Search."
    )
    subject: str = Field(
        description="The academic subject or category (e.g., 'math', 'physics', 'chemistry', 'literature', etc.)."
    )


class OCRResponse(BaseModel):
    summary: str = Field(
        description="A short title-like summary of the image content, e.g. 'Calculus integration exercise, page 5'."
    )
    subject: str = Field(
        description="The academic subject of the content, e.g. 'math', 'physics', 'chemistry', 'literature', 'biology'. Use 'unknown' if unclear."
    )
    tags: list[str] = Field(
        description="A list of relevant keywords extracted from the content, e.g. ['integration', 'grade 12', 'definite integral']. Keep each tag short."
    )
    detail: str = Field(
        description="The complete and detailed transcription of the image, including LaTeX for math, Markdown for tables, and descriptions for diagrams as requested in the system prompt."
    )
    has_diagram: bool = Field(
        description="True if the image contains any diagram, graph, chart, or figure."
    )
    has_table: bool = Field(
        description="True if the image contains a table or grid of data."
    )
    confidence: float = Field(
        description="A confidence score between 0.0 and 1.0. 1.0 means perfectly clear, 0.5 means some parts are blurry or illegible, and below 0.3 means the content is mostly unreadable."
    )
    reasoning: str = Field(
        description="A brief explanation for the confidence score (e.g., 'Image is slightly blurry at the edges' or 'Handwriting is clear')."
    )
    diagram_detection: List[BoundingBox] = Field(
        description="""
    Case 1: If there are no diagram, return empty list.
    Case 2: Detect all distinct exercise blocks, diagrams, or tables in this image.
    For each item, identify its bounding box [ymin, xmin, ymax, xmax] on a scale of 0 to 1000.
    Provide a label and a content_summary for each.
    If a diagram is related to an exercise, detect them as separate blocks but mention the relationship in the summary."""
    )


class FileService:
    def __init__(self, files: list[discord.Attachment]):
        for file in files:
            if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise (
                    f"❌ `{file.filename}` quá lớn "
                    f"({file.size / 1024 / 1024:.1f}MB). "
                    f"Max: {MAX_FILE_SIZE_MB}MB"
                )
            mime = file.content_type or "application/octet-stream"
            if not mime.startswith("image/"):
                raise (
                    f"❌ `{file.filename}` có định dạng không được hỗ trợ "
                    f"(MIME type: {mime}). "
                    f"Chỉ hỗ trợ hình ảnh."
                )
        self.files = files
        self.ocr_response: OCRResponse | None = None
        self.file_embedding_data: list[float] | None = None

    async def extract_files_data(
        self,
    ):
        # TODO: to parallel if there are multiple files
        for file in self.files:
            file_name = random_filename_from_url(file.url)
            file_path = await save_image(file.url, CACHE_FILE_FOLDER_PATH + file_name)
            if not file_path:
                raise Exception("Can not download file")
            mime = file.content_type

            if mime.startswith("image/"):
                # self.file_embedding_data = await self.embed_file(file_path)
                self.ocr_response = await self.ocr_image(file_path)
                print("ocr_response", self.ocr_response)
                self.process_multi_images(
                    file_path, self.ocr_response.diagram_detection
                )

    async def ocr_image(self, file_path: str) -> OCRResponse:
        """Dùng Gemini Vision để extract toàn bộ nội dung từ ảnh."""

        file = await aclient.files.upload(file=file_path)
        response = await aclient.models.generate_content(
            model=env.GEMINI_LITE_MODEL,
            contents=[
                file,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=OCRResponse,
                temperature=0,
            ),
        )

        return OCRResponse.model_validate_json(response.text)

    async def embed_file(self, file_path: str):
        """Dùng Gemini Text Embed để tạo embedding cho file đã extract."""
        with open(file_path, "rb") as f:
            image_data = f.read()

        response = await aclient.models.embed_content(
            model=env.GEMINI_EMBED_MODEL,
            contents=types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT", output_dimensionality=768
            ),
        )
        return response.embeddings[0].values

    def process_multi_images(
        self, original_image_path: str, ai_detected_items: List[BoundingBox]
    ):
        img = Image.open(original_image_path)
        width, height = img.size

        cropped_files = []

        for item in ai_detected_items:
            coords = item.box_2d
            label = item.label

            # Tính toán pixel
            top = (coords[0] / 1000) * height
            left = (coords[1] / 1000) * width
            bottom = (coords[2] / 1000) * height
            right = (coords[3] / 1000) * width

            # Crop và lưu
            crop = img.crop((left, top, right, bottom))
            crop_name = f"{label.replace(' ', '_')}.jpg"
            crop.save(crop_name)

            cropped_files.append({"label": label, "path": crop_name})

        return cropped_files

    async def store_files(self, user_discord_id: int, channel_id: int, guild_id: int):
        await ExtractFileRecords(
            user_discord_id=user_discord_id,
            guild_id=guild_id,
            channel_id=channel_id,
            s3_key="test1",
            s3_pre_process_key="test2",
            **self.ocr_response.model_dump(exclude={"reasoning"}),
            embedding_vector=self.file_embedding_data,
        ).insert()

    async def check_file_duplicate(
        self, embedding_vector: list[float], threshold: float = 0.9
    ):
        pass

    @staticmethod
    async def embed_text(query: str) -> list[float]:
        """Embed text query using Gemini Text Embed."""
        response = await aclient.models.embed_content(
            model=env.GEMINI_EMBED_MODEL,
            contents=types.Content(role="user", parts=[types.Part(text=query)]),
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT", output_dimensionality=768
            ),
        )
        return response.embeddings[0].values

    @staticmethod
    async def vector_search(
        query_embedding: list[float],
        user_discord_id: int | None = None,
        top_k: int = 20,
    ) -> list[dict]:
        """Vector search using MongoDB Atlas Vector Search."""
        vector_search_stage = {
            "index": "vector_index",
            "path": "embedding_vector",
            "queryVector": query_embedding,
            "numCandidates": 100,
            "limit": top_k,
        }
        # Only add filter if user_discord_id is provided and index supports it
        if user_discord_id is not None:
            vector_search_stage["filter"] = {
                "user_discord_id": {"$eq": user_discord_id},
            }

        pipeline = [
            {"$vectorSearch": vector_search_stage},
            {"$addFields": {"vector_score": {"$meta": "vectorSearchScore"}}},
        ]

        results = await ExtractFileRecords.aggregate(pipeline).to_list()
        # Add vector_rank for RRF
        for rank, doc in enumerate(results):
            doc["vector_rank"] = rank
        return results

    @staticmethod
    async def fulltext_search(
        query: str,
        user_discord_id: int,
        top_k: int = 20,
        index_name: str = "fulltext_index",
    ) -> list[dict]:
        """Full-text search using MongoDB Atlas Search with fuzzy matching."""
        pipeline = [
            {
                "$search": {
                    "index": index_name,
                    "compound": {
                        "must": [
                            {
                                "text": {
                                    "query": query,
                                    "path": ["detail", "summary", "tags"],
                                    "fuzzy": {"maxEdits": 1},
                                }
                            }
                        ],
                        "filter": [
                            {
                                "equals": {
                                    "path": "user_discord_id",
                                    "value": user_discord_id,
                                }
                            }
                        ],
                    },
                }
            },
            {"$limit": top_k},
            {
                "$addFields": {
                    "text_score": {"$meta": "searchScore"},
                }
            },
        ]

        results = await ExtractFileRecords.aggregate(pipeline).to_list()
        # Add text_rank for RRF
        for rank, doc in enumerate(results):
            doc["text_rank"] = rank
        return results

    @staticmethod
    def reciprocal_rank_fusion(
        vector_results: list[dict],
        text_results: list[dict],
        k: int = 60,
        top_n: int = 8,
    ) -> list[dict]:
        """
        Merge vector + BM25 results bằng RRF.

        Score = 1/(k + rank_vector) + 1/(k + rank_text)

        k=60 là default ổn cho hầu hết case.
        Tăng k → flatten (ít ưu tiên top rank hơn).
        Giảm k → aggressive với top rank.
        """
        scores: dict[str, float] = {}
        docs: dict[str, dict] = {}

        # Accumulate từ vector results
        for doc in vector_results:
            doc_id = str(doc["_id"])
            rank = doc.get("vector_rank", 0)
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
            docs[doc_id] = doc

        # Accumulate từ text results
        for doc in text_results:
            doc_id = str(doc["_id"])
            rank = doc.get("text_rank", 0)
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
            if doc_id not in docs:
                docs[doc_id] = doc

        # Sort by RRF score
        ranked_ids = sorted(scores, key=lambda x: scores[x], reverse=True)

        results = []
        for doc_id in ranked_ids[:top_n]:
            doc = docs[doc_id]
            doc["rrf_score"] = scores[doc_id]
            results.append(doc)

        return results

    @staticmethod
    async def search(
        query: str,
        limit: int = 5,
        user_discord_id: int | None = None,
    ) -> list[dict]:
        """
        Backward-compatible search function.
        Uses vector search only (no RRF) for simple use cases.
        """
        query_embedding = await FileService.embed_text(query)
        results = await FileService.vector_search(
            query_embedding, user_discord_id=user_discord_id, top_k=limit
        )
        return results

    @staticmethod
    async def retrieve_relevant_facts(
        query: str,
        user_discord_id: int,
        top_n: int = 8,
        min_confidence: float = IMAGE_EXTRACT_CONFIDENCE_THRESHOLD,
    ) -> list[dict]:
        """
        Full hybrid search pipeline:
          1. Embed query
          2. Vector search + BM25 search (song song)
          3. RRF fusion
          4. Filter theo confidence

        Trả về list facts sẵn sàng inject vào prompt.
        """
        # Chạy song song 2 search để giảm latency
        query_embedding, text_results = await asyncio.gather(
            FileService.embed_text(query),
            FileService.fulltext_search(query, user_discord_id, top_k=20),
        )

        vector_results = await FileService.vector_search(
            query_embedding, user_discord_id=user_discord_id, top_k=20
        )

        # Fuse
        fused = FileService.reciprocal_rank_fusion(
            vector_results, text_results, top_n=top_n
        )

        # Filter fact có confidence quá thấp
        filtered = [f for f in fused if f.get("confidence", 1.0) >= min_confidence]

        return filtered


class ExtractFileRecordsQuery:
    def __init__(self, files: list[ExtractFileRecords]):
        self.files = files

    @classmethod
    async def fetch(
        cls,
        user_discord_id: int,
        channel_id: int,
        limit: int = 5,
    ) -> "ExtractFileRecordsQuery":
        files = (
            await ExtractFileRecords.find(
                ExtractFileRecords.user_discord_id == user_discord_id,
                ExtractFileRecords.channel_id == channel_id,
            )
            .sort(-ExtractFileRecords.id)
            .limit(limit)
            .to_list()
        )
        return cls(files or [])

    def _to_dicts(self) -> list[dict]:
        return [
            {
                **file.model_dump(
                    include={
                        "summary",
                        "detail",
                        "subject",
                        "tags",
                        "has_diagram",
                        "has_table",
                    }
                ),
                "id": str(file.id),
            }
            for file in self.files
        ]

    def to_object_list(self) -> list[dict]:
        return self._to_dicts()

    def to_json(self) -> str:
        return json.dumps(self._to_dicts(), ensure_ascii=False, indent=2)
