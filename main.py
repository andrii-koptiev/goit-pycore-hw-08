from functools import wraps
from typing import Any, Callable

from address_book import AddressBook
from models import Record
from serialization import load_data, save_data

Args = list[str]


COMMANDS: list[tuple[str, str]] = [
    ("hello", "greet the bot"),
    ("add <name> <phone>", "create a record or add a phone to an existing one"),
    ("change <name> <old_phone> <new_phone>", "replace a phone of a record"),
    ("phone <name>", "show the phones of a record"),
    ("all", "show all records"),
    ("add-birthday <name> <DD.MM.YYYY>", "set the birthday of a record"),
    ("show-birthday <name>", "show the birthday of a record"),
    ("birthdays", "show birthdays in the next 7 days"),
    ("help", "show this list of commands"),
    ("close | exit", "leave the bot"),
]

PROMPT = "Enter a command: "
UPCOMING_DAYS = 7
MISSING_ARGUMENT_MESSAGE = "Enter the argument for the command"
NOT_FOUND_MESSAGE = "Contact not found."
GOODBYE_MESSAGE = "Good bye!"


def input_error(func: Callable[..., str]) -> Callable[..., str]:
    """Decorate a command handler to turn input errors into messages.

    IndexError means an argument is missing. ValueError carries a ready
    message from the model (bad phone, bad date, duplicate...) and is shown
    as is. KeyError means the record does not exist. The message is
    returned, not printed, so the bot shows it like any other reply and keeps
    running.

    Args:
        func: Command handler that returns the reply for the user.

    Returns:
        Wrapped handler with the same name and docstring as func.
    """

    @wraps(func)
    def inner(*args: Any, **kwargs: Any) -> str:
        """Call func and return a message if the user input was wrong."""
        try:
            return func(*args, **kwargs)
        except IndexError:
            return MISSING_ARGUMENT_MESSAGE
        except ValueError as error:
            return str(error)
        except KeyError:
            return NOT_FOUND_MESSAGE

    return inner


def parse_input(user_input: str) -> tuple[str, Args]:
    """Split a line of user input into a command and its arguments.

    Args:
        user_input: Raw line typed by the user.

    Returns:
        The case-folded command and its arguments; ("", []) for a blank line.
    """
    parts = user_input.split()
    if not parts:
        return "", []
    cmd, *args = parts
    return cmd.casefold(), args


def get_record(book: AddressBook, name: str) -> Record:
    """Return the record for name or raise KeyError if there is none."""
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    return record


@input_error
def add_record(args: Args, book: AddressBook) -> str:
    """Create a record, or add a phone to an existing one.

    Args:
        args: [name, phone]; a missing item raises IndexError.
        book: Address book, changed in place.

    Returns:
        A confirmation. An invalid or duplicate phone raises ValueError.
    """
    name, phone = args[0], args[1]
    record = book.find(name)
    if record is not None:
        record.add_phone(phone)
        return "Contact updated."

    # Fill the record first so a bad phone does not leave an empty record.
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."


@input_error
def change_record(args: Args, book: AddressBook) -> str:
    """Replace one phone of an existing record.

    Args:
        args: [name, old_phone, new_phone]; a missing item raises IndexError.
        book: Address book, changed in place.

    Returns:
        A confirmation. An unknown name raises KeyError; an unknown old phone
        or an invalid new phone raises ValueError.
    """
    name, old_phone, new_phone = args[0], args[1], args[2]
    get_record(book, name).edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args: Args, book: AddressBook) -> str:
    """Return the phones of a record.

    Args:
        args: The name comes first; an empty list raises IndexError.
        book: Address book.

    Returns:
        The phones separated by "; ". An unknown name raises KeyError.
    """
    record = get_record(book, args[0])
    return "; ".join(str(phone) for phone in record.phones) or "No phones."


@input_error
def show_all(book: AddressBook) -> str:
    """Return all records, one line each.

    Args:
        book: Address book.

    Returns:
        The records in insertion order, or a notice if there are none.
    """
    if not book.data:
        return "No contacts."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args: Args, book: AddressBook) -> str:
    """Set the birthday of a record.

    Args:
        args: [name, birthday]; a missing item raises IndexError.
        book: Address book, changed in place.

    Returns:
        A confirmation. An unknown name raises KeyError; a bad date raises
        ValueError.
    """
    name, birthday = args[0], args[1]
    get_record(book, name).add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args: Args, book: AddressBook) -> str:
    """Return the birthday of a record.

    Args:
        args: The name comes first; an empty list raises IndexError.
        book: Address book.

    Returns:
        The birthday, or a notice if none is set. An unknown name raises
        KeyError.
    """
    record = get_record(book, args[0])
    if record.birthday is None:
        return "Birthday is not set."
    return str(record.birthday)


@input_error
def birthdays(args: Args, book: AddressBook) -> str:
    """Return who to congratulate in the next UPCOMING_DAYS days.

    Birthdays on a weekend are moved to the following Monday.

    Args:
        args: Not used; accepted so every handler is called the same way.
        book: Address book.

    Returns:
        One "name: congratulation date" line per record, soonest first, or a
        notice.
    """
    upcoming = book.get_upcoming_birthdays(UPCOMING_DAYS)
    if not upcoming:
        return f"No birthdays in the next {UPCOMING_DAYS} days."
    return "\n".join(
        f"{item.record.name.value}: {item.congratulation_date.strftime('%d.%m.%Y')}"
        for item in upcoming
    )


@input_error
def show_help() -> str:
    """Return the list of available commands."""
    width = max(len(usage) for usage, _ in COMMANDS)
    lines = [f"{usage:<{width}}  {description}" for usage, description in COMMANDS]
    return "\n".join(["Available commands:", *lines])


def handle_command(command: str, args: Args, book: AddressBook) -> str:
    """Run one command and return the reply for the user."""
    if command == "hello":
        return "How can I help you?"
    if command == "add":
        return add_record(args, book)
    if command == "change":
        return change_record(args, book)
    if command == "phone":
        return show_phone(args, book)
    if command == "all":
        return show_all(book)
    if command == "add-birthday":
        return add_birthday(args, book)
    if command == "show-birthday":
        return show_birthday(args, book)
    if command == "birthdays":
        return birthdays(args, book)
    if command == "help":
        return show_help()
    return "Invalid command. Type 'help' to see the commands."


def main() -> None:
    """Read commands from the user until "close", "exit", Ctrl+C or Ctrl+D."""
    book = load_data()
    print("Welcome to the assistant bot!")

    try:
        while True:
            try:
                command, args = parse_input(input(PROMPT))
            except (KeyboardInterrupt, EOFError):
                # Ctrl+C / Ctrl+D leave the prompt line unfinished; move to a new one.
                print()
                break

            if not command:
                continue

            if command in ("close", "exit"):
                break

            print(handle_command(command, args, book))
    finally:
        # Runs on every way out, including an unexpected error.
        save_data(book)

    print(GOODBYE_MESSAGE)


if __name__ == "__main__":
    main()
