# default
from typing import List, Optional

# lib
from beanie import Document
from google.generativeai import protos
from pydantic import BaseModel


class FileData(BaseModel):
    mime_type: str
    file_uri: str


class Content(BaseModel):
    text: Optional[str] = None
    file_data: Optional[FileData] = None
    # TODO: validate 2 field cannot be empty


class UserAIChatHistory(Document):
    model_type: str

    created_by: int
    channel_id: int
    contents: List[Content]
    response: str

    @staticmethod
    async def get_history(
        user_id: int, channel_id: int, limit=15, without_files: List[str] = []
    ):
        model_histories = await UserAIChatHistory.find(
            {"created_by": user_id, "channel_id": channel_id}, limit=limit
        ).to_list()

        # TODO: refactor
        histories = [
            protos.Content(
                parts=[
                    {
                        "text": "Answer in Vietnamese except there are request to answer in other language above. The answer must be shorter than 1500 letters(include space). REMEMBER shorter than 1500 letters, not words. If the answer longer then shorten the answer. No yapping"
                    }
                ],
                role="user",
            )
        ]
        for history in model_histories:
            contents = []
            for content in history.contents:
                if content.text:
                    contents.append({"text": content.text})
                elif content.file_data:
                    file_uri = content.file_data.file_uri
                    if any(part in file_uri for part in without_files):
                        continue
                    contents.append(
                        {
                            "file_data": {
                                "mime_type": content.file_data.mime_type,
                                "file_uri": file_uri,
                            }
                        }
                    )

                histories.append(protos.Content(parts=contents, role="user"))

            histories.append(
                protos.Content(parts=[{"text": history.response}], role="model")
            )

        return histories
