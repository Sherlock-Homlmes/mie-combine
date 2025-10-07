# default
import datetime
from enum import Enum
from typing import Optional

import pymongo

# lib
from beanie import Document, Indexed

# local


class CurrencyUnitEnum(str, Enum):
    VND = "VNĐ"
    BTM_TOKEN = "BTM"


currency_unit_decimals = {
    CurrencyUnitEnum.VND: 0,
    CurrencyUnitEnum.BTM_TOKEN: 0,
}


class Transactions(Document):
    from_user_id: Indexed(int, index_type=pymongo.DESCENDING)
    to_user_id: Indexed(int, index_type=pymongo.DESCENDING)

    amount: float
    currency_unit: CurrencyUnitEnum
    message: Optional[str] = None

    created_at: Indexed(datetime.datetime, index_type=pymongo.DESCENDING)
