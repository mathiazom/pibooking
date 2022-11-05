import json
from enum import Enum, auto


class BookingError(Enum):
    ERROR = auto()
    MALFORMED_SEARCH = auto()
    MALFORMED_SCHEDULE = auto()
    MISSING_SCHEDULE_DAY = auto()
    INCORRECT_START_TIME = auto()
    CLASS_MISSING = auto()
    MALFORMED_CLASS = auto()
    TOO_LONG_WAITING_TIME = auto()
    INVALID_CONFIG = auto()
    NOT_OPEN_FOR_BOOKING = auto()
    OVERLAPPING_BOOKING = auto()


IBOOKING_ERROR_CODE_TO_BOOKING_ERROR = {
    1035: BookingError.NOT_OPEN_FOR_BOOKING,
    1013: BookingError.OVERLAPPING_BOOKING
}


def booking_error_from_ibooking_response_text(response_text: str):
    error_code = json.loads(response_text)["errorCode"]
    if error_code not in IBOOKING_ERROR_CODE_TO_BOOKING_ERROR:
        return BookingError.ERROR
    return IBOOKING_ERROR_CODE_TO_BOOKING_ERROR[error_code]
