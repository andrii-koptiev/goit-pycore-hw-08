from datetime import date, datetime
from typing import Any, Optional


class Field:
    """Base class representing a generic data field."""

    def __init__(self, value: Any, required: bool = False) -> None:
        self.value: Any = value
        self.required: bool = required

    def __str__(self) -> str:
        return str(self.value) if self.value is not None else "-"


class Name(Field):
    """Inherited class specifically for names (Required)."""

    def __init__(self, value: str) -> None:
        # Enforce that value must be a string and required is True
        super().__init__(value=value, required=True)

        # Simple validation block
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name field cannot be empty.")

    # Add name-specific functionality
    def to_uppercase(self) -> str:
        return self.value.upper()


class Phone(Field):
    """Phone number (optional): if given, must be exactly 10 ASCII digits."""

    def __init__(self, value: Optional[str] = None, required: bool = False) -> None:
        super().__init__(value=value, required=required)

        if value is None:
            if required:
                raise ValueError("Phone is required but no value was given.")
            return

        if not isinstance(value, str) or not (value.isascii() and value.isdigit()):
            raise ValueError("Phone number must contain only digits")
        if len(value) != 10:
            raise ValueError("Phone number should be 10 digits long")


class Birthday(Field):
    """Birthdate (optional): should be provided in valid format."""

    FORMAT = "%d.%m.%Y"
    AGE_GAP_YEARS = 120

    def __init__(self, value: str) -> None:
        try:
            parsed = datetime.strptime(value, self.FORMAT).date()
        except (ValueError, TypeError):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

        today = date.today()
        if parsed > today:
            raise ValueError("Birthday cannot be in the future")

        try:
            oldest = today.replace(year=today.year - self.AGE_GAP_YEARS)
        except ValueError:  # today is Feb 29, target year is not a leap year
            oldest = today.replace(year=today.year - self.AGE_GAP_YEARS, day=28)
        if parsed < oldest:
            raise ValueError(
                f"Birthday cannot be more than {self.AGE_GAP_YEARS} years in the past"
            )

        super().__init__(parsed)

    def next_occurrence(self, today: date) -> date:
        birthday = self._get_next_birthday_date(self.value, today.year)
        if birthday < today:
            return self._get_next_birthday_date(self.value, today.year + 1)
        return birthday

    @staticmethod
    def _get_next_birthday_date(date_of_birth: date, year: int) -> date:
        try:
            return date_of_birth.replace(year=year)
        except ValueError:  # 29 February in a non-leap year moved to March 1
            return date(year, 3, 1)

    def __str__(self) -> str:
        return self.value.strftime(self.FORMAT)
