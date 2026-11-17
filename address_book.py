from collections import UserDict
from datetime import date
from typing import Optional

from models import Record, UpcomingBirthday


class AddressBook(UserDict[str, Record]):
    """Collection of records, keyed by record name."""

    def add_record(self, new_record: Record) -> None:
        name = new_record.name.value
        if name in self.data:
            raise ValueError(f"Contact {name} already exists.")
        self.data[name] = new_record

    def find(self, name: str) -> Optional[Record]:
        return self.data.get(name)

    def delete(self, name: str) -> None:
        if name not in self.data:
            raise ValueError(f"Contact {name} not found.")
        del self.data[name]

    def get_upcoming_birthdays(self, days_interval: int) -> list[UpcomingBirthday]:
        today = date.today()
        upcoming_birthdays: list[UpcomingBirthday] = []

        if days_interval < 0:
            raise ValueError("Days must be 0 or more")

        for record in self.data.values():
            if record.birthday is None:
                continue

            next_birthday = record.birthday.next_occurrence(today)
            if 0 <= (next_birthday - today).days <= days_interval:
                upcoming_birthdays.append(UpcomingBirthday(record, next_birthday))

        return sorted(upcoming_birthdays, key=lambda upcoming: (upcoming.congratulation_date, upcoming.record.name.value),
        )
