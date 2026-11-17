import os
import pickle
from pathlib import Path

from address_book import AddressBook

# Next to the code, so the book is the same whatever directory the bot starts in.
DEFAULT_FILENAME = Path(__file__).resolve().parent / "addressbook.pkl"
CORRUPT_SUFFIX = ".corrupt"

# What pickle.load can raise on an empty, truncated or incompatible file.
_LOAD_ERRORS = (
    pickle.UnpicklingError,
    EOFError,
    AttributeError,
    ImportError,
    IndexError,
    TypeError,
)


def save_data(book: AddressBook, filename: str | Path = DEFAULT_FILENAME) -> None:
    """Pickle the address book to filename.

    The data goes to a temporary file first and replaces the old file in one
    step, so a crash while saving cannot destroy the previous book.

    Args:
        book: Address book to store.
        filename: Path of the pickle file.
    """
    path = Path(filename)
    temp_path = path.with_name(path.name + ".tmp")
    try:
        with open(temp_path, "wb") as file:
            pickle.dump(book, file)
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def load_data(filename: str | Path = DEFAULT_FILENAME) -> AddressBook:
    """Load the address book from filename.

    A missing file gives a new empty book. An unreadable file (empty,
    truncated, not an AddressBook) is moved aside to "<filename>.corrupt" so
    the bot can start and the bad data is not overwritten.

    Only load files this bot wrote: unpickling can run arbitrary code.

    Args:
        filename: Path of the pickle file.

    Returns:
        The stored address book, or a new empty one.
    """
    path = Path(filename)
    try:
        with open(path, "rb") as file:
            book = pickle.load(file)
    except FileNotFoundError:
        return AddressBook()
    except _LOAD_ERRORS:
        book = None

    if isinstance(book, AddressBook):
        return book

    backup = path.with_name(path.name + CORRUPT_SUFFIX)
    os.replace(path, backup)
    print(f"Could not read {path.name}; moved it to {backup.name}. Starting empty.")
    return AddressBook()
