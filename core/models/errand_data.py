# default
from typing import Any

# lib
from beanie import Document


class ErrandData(Document):
    name: str
    value: Any
