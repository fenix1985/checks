from enum import Enum

from utils import camelcase_to_snake


class BaseStringEnum(str, Enum):
    @classmethod
    def from_str(cls, label: str):
        return cls._value2member_map_[label]

    @classmethod
    def get_name(cls):

        return camelcase_to_snake(cls.__name__)


class PaymentType(BaseStringEnum):
    CASH = "cash"
    CASHLESS = "cashless"
