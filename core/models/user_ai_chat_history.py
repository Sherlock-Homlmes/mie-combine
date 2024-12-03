# default
from typing import Optional, List

# lib
from beanie import Document
from pydantic import BaseModel
from google.generativeai import protos


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
    async def get_history(user_id: int, channel_id: int, limit=10):
        model_histories = await UserAIChatHistory.find(
            {"created_by": user_id, "channel_id": channel_id}, limit=limit
        ).to_list()

        # TODO: refactor
        histories = []
        for history in model_histories:
            contents = []
            for content in history.contents:
                if content.text:
                    contents.append({"text": content.text})
                elif content.file_data:
                    contents.append(
                        {
                            "file_data": {
                                "mime_type": content.file_data.mime_type,
                                "file_uri": content.file_data.file_uri,
                            }
                        }
                    )

                histories.append(protos.Content(parts=contents, role="user"))

            histories.append(protos.Content(parts=[{"text": history.response}], role="model"))

        return histories
