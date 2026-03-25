"""
Handles file upload, text extraction, chunking, and embedding pipeline.
"""

import json

from google.genai import types
from pydantic import BaseModel, Field

from core.env import env
from models import ExtractFileRecords
from utils.ai_coversation import aclient

TEXT_EXTENSIONS = {"txt", "md", "py", "js", "ts", "json", "csv"}
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
CHUNK_SIZE = 1500  # characters per chunk
CHUNK_OVERLAP = 200
MAX_FILE_SIZE_MB = 8
IMAGE_EXTRACT_CONFIDENCE_THRESHOLD = 0.7
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


async def extract_image_to_text(file_path: str) -> str:
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
            temperature=0.1,
        ),
    )

    return OCRResponse.model_validate_json(response.text)


def check_file_validation(files):
    for file in files:
        if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise (
                f"❌ `{file.filename}` quá lớn "
                f"({file.size / 1024 / 1024:.1f}MB). "
                f"Max: {MAX_FILE_SIZE_MB}MB"
            )


async def add_file_record(
    user_discord_id: int,
    channel_id: int,
    guild_id: int,
    file_path: str,
    original_filename: str,
    extracted: OCRResponse,
):
    print("adding file record")

    await ExtractFileRecords(
        user_discord_id=user_discord_id,
        guild_id=guild_id,
        channel_id=channel_id,
        original_filename=original_filename,
        s3_key="test",
        **extracted.model_dump(exclude={"reasoning"}),
    ).insert()


# def _extract_text_from_bytes(data: bytes, filename: str) -> str:
#     ext = Path(filename).suffix.lower().lstrip(".")

#     if ext in TEXT_EXTENSIONS:
#         return data.decode("utf-8", errors="ignore")

#     if ext == "pdf":
#         try:
#             import pypdf

#             reader = pypdf.PdfReader(io.BytesIO(data))
#             return "\n".join(page.extract_text() or "" for page in reader.pages)
#         except Exception as e:
#             print(f"PDF extraction failed for {filename}: {e}", flush=True)
#             return ""

#     return ""

# def _chunk_text(text: str, filename: str) -> list[str]:
#     if not text.strip():
#         return []
#     chunks = []
#     start = 0
#     while start < len(text):
#         end = start + CHUNK_SIZE
#         chunk = text[start:end]
#         if chunk.strip():
#             chunks.append(chunk)
#         start = end - CHUNK_OVERLAP
#     return chunks


# async def process_and_embed_file(
#     file_data: bytes,
#     filename: str,
#     user_id: str,
#     guild_id: str,
#     channel_id: str,
#     mime_type: str = None,
#     extracted_text: str = None,  # text đã extract sẵn (tránh gọi Gemini 2 lần)
# ) -> FileRecord:
#     ext = Path(filename).suffix.lower().lstrip(".")

#     if ext not in settings.allowed_ext_list:
#         raise ValueError(f"File type `.{ext}` is not allowed.")

#     if len(file_data) > settings.max_file_size_bytes:
#         raise ValueError(
#             f"File too large ({len(file_data) / 1024 / 1024:.1f}MB). "
#             f"Max allowed: {settings.max_file_size_mb}MB"
#         )

#     mime_type = (
#         mime_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
#     )

#     # Upload to R2
#     file_id = str(uuid.uuid4())
#     r2_key = f"{settings.r2_files_prefix}/{guild_id}/{user_id}/{file_id}_{filename}"
#     await r2_service.upload_file(r2_key, file_data, mime_type)
#     logger.info(f"Uploaded file to R2: {r2_key}")

#     # Create FileRecord
#     record = FileRecord(
#         user_id=user_id,
#         guild_id=guild_id,
#         channel_id=channel_id,
#         original_filename=filename,
#         r2_key=r2_key,
#         file_size=len(file_data),
#         mime_type=mime_type,
#     )
#     await record.insert()

#     # Extract text và embed
#     if extracted_text is not None:
#         text = extracted_text  # dùng text đã extract sẵn, không gọi lại
#     elif mime_type and mime_type.startswith("image/"):
#         text = await extract_image_text(file_data, mime_type, filename)
#     else:
#         text = _extract_text_from_bytes(file_data, filename)
#     chunks = _chunk_text(text, filename)

#     if chunks:
#         chunk_payloads = [
#             {
#                 "file_record_id": str(record.id),
#                 "r2_key": r2_key,
#                 "user_id": user_id,
#                 "guild_id": guild_id,
#                 "chunk_index": i,
#                 "content": chunk,
#                 "metadata": {"filename": filename, "mime_type": mime_type},
#             }
#             for i, chunk in enumerate(chunks)
#         ]
#         chunk_ids = await embed_service.embed_chunks(chunk_payloads)
#         record.embedded = True
#         record.embed_chunk_ids = chunk_ids
#         await record.save()
#         logger.info(f"Embedded {len(chunk_ids)} chunks for file {filename}")
#     else:
#         logger.warning(f"No text extracted from {filename}, skipping embedding")

#     return record


# async def reembed_missing_files(guild_id: str = None) -> dict:
#     """
#     Find files in R2 that aren't embedded in LanceDB and re-embed them.
#     Called from the recovery bash script.
#     """
#     embedded_keys = await embed_service.get_all_embedded_r2_keys()

#     # Get all file records from MongoDB
#     query = {}
#     if guild_id:
#         query["guild_id"] = guild_id

#     all_records = await FileRecord.find_all().to_list()
#     missing = [r for r in all_records if r.r2_key not in embedded_keys]

#     results = {
#         "total": len(all_records),
#         "missing": len(missing),
#         "reembedded": 0,
#         "errors": [],
#     }

#     for record in missing:
#         try:
#             data = await r2_service.download_file(record.r2_key)
#             text = _extract_text_from_bytes(data, record.original_filename)
#             chunks = _chunk_text(text, record.original_filename)

#             if chunks:
#                 chunk_payloads = [
#                     {
#                         "file_record_id": str(record.id),
#                         "r2_key": record.r2_key,
#                         "user_id": record.user_id,
#                         "guild_id": record.guild_id,
#                         "chunk_index": i,
#                         "content": chunk,
#                         "metadata": {"filename": record.original_filename},
#                     }
#                     for i, chunk in enumerate(chunks)
#                 ]
#                 chunk_ids = await embed_service.merge_and_reembed(chunk_payloads)
#                 record.embedded = True
#                 record.embed_chunk_ids = chunk_ids
#                 await record.save()
#                 results["reembedded"] += 1
#                 logger.info(f"Re-embedded: {record.original_filename}")
#         except Exception as e:
#             err = f"{record.original_filename}: {e}"
#             results["errors"].append(err)
#             logger.error(f"Failed to re-embed {record.r2_key}: {e}")

#     return results
