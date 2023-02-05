from beanie import Document


class Confessions(Document):
    channel_id: str
    member_id: str
    type: str
