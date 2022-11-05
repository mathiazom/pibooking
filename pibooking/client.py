import time
import warnings
from typing import Optional

import requests

from pibooking.consts import ADD_BOOKING_URL, TOKEN_VALIDATION_URL
from pibooking.errors import BookingError, booking_error_from_ibooking_response_text
from pibooking.logging import get_logger

_LOGGER = get_logger(__name__)


class IBookingClient:
    def __init__(self, url: str, token: str):
        self.url = url
        self._validate_token(token)
        self.token = token

    def _api_url(self, url):
        return self.url + url

    def _validate_token(self, token: str):
        token_validation = requests.post(self._api_url(TOKEN_VALIDATION_URL), {"token": token})
        if token_validation.status_code != requests.codes.OK:
            raise Exception(f"Validation of authentication token failed:  {token_validation.text}")
        token_info = token_validation.json()
        if 'info' in token_info and token_info['info'] == "client-readonly":
            raise Exception("Authentication failed, only acquired public readonly access")
        if 'user' not in token_info or token_info['user'] is None:
            raise Exception("Authentication failed")

    def book_class(self, class_id: str, max_attempts: int = 5) -> Optional[BookingError]:
        if max_attempts < 1:
            warnings.warn(f"Max booking attempts should be a positive number, was {max_attempts}")
            return
        booked = False
        attempts = 0
        booking_error = None
        while not booked:
            booking_error = self._book_class(class_id)
            attempts += 1
            if not booking_error:
                booked = True
                break
            if booking_error in [BookingError.OVERLAPPING_BOOKING]:
                break
            if attempts >= max_attempts:
                break
            sleep_seconds = 2 ** attempts
            _LOGGER.info(f"Exponential backoff, retrying in {sleep_seconds} seconds...")
            time.sleep(sleep_seconds)
        if not booked:
            _LOGGER.error(f"Booking failed after {attempts} attempt" + ("s" if attempts != 1 else ""))
            if booking_error is not None:
                return booking_error
            return BookingError.ERROR
        _LOGGER.info(f"Successfully booked class" + (f" after {attempts} attempts!" if attempts != 1 else "!"))
        return None

    def _book_class(self, class_id: str) -> Optional[BookingError]:
        _LOGGER.info(f"Booking class {class_id}")
        response = requests.post(
            self._api_url(ADD_BOOKING_URL),
            {
                "classId": class_id,
                "token": self.token
            }
        )
        if response.status_code != requests.codes.OK:
            _LOGGER.error("Booking attempt failed: " + response.text)
            return booking_error_from_ibooking_response_text(response.text)
