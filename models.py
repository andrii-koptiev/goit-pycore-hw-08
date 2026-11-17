from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from fields import Birthday, Name, Phone


class Record:
    """A record: one required name and a list of phone numbers."""

    def __init__(self, name: str) -> None:
        self.name: Name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Optional[Birthday] = None

    def add_phone(self, phone: str) -> None:
        new_phone = Phone(phone)
        if self.find_phone(new_phone.value) is not None:
            raise ValueError(f"Phone {phone} already exists.")
        self.phones.append(new_phone)

    def remove_phone(self, phone_to_remove: str) -> None:
        phone = self.find_phone(phone_to_remove)
        if phone is None:
            raise ValueError(f"Phone {phone_to_remove} not found.")
        self.phones.remove(phone)

    def edit_phone(self, phone_to_edit: str, new_phone: str) -> None:
        for index, phone in enumerate(self.phones):
            if phone.value == phone_to_edit:
                self.phones[index] = Phone(new_phone)
                return
        raise ValueError(f"Phone {phone_to_edit} not found.")

    def find_phone(self, phone_to_found: str) -> Optional[Phone]:
        for phone in self.phones:
            if phone.value == phone_to_found:
                return phone
        return None

    def add_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

    def __str__(self) -> str:
        result = f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}"
        if self.birthday:
            result += f", birthday: {self.birthday}"
        return result


@dataclass
class UpcomingBirthday:
    record: Record
    next_birthday: date

    @property
    def congratulation_date(self) -> date:
        """The day to congratulate: weekend birthdays move to Monday."""
        weekday = self.next_birthday.weekday()  # Monday is 0, Sunday is 6
        if weekday >= 5:
            return self.next_birthday + timedelta(days=7 - weekday)
        return self.next_birthday
