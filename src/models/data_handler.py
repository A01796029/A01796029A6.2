import json
import os


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
HOTELS_FILE = os.path.join(DATA_DIR, "hotels.json")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")
RESERVATIONS_FILE = os.path.join(DATA_DIR, "reservations.json")

def _ensure_data_dir():
    """Create data directory if it does not exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json(filepath):
    """Load JSON data from file, returning empty dict on error."""
    _ensure_data_dir()
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object at root level.")
            return data
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR loading {filepath}: {exc}. Starting with empty dataset.")
        return {}


def save_json(filepath, data):
    """Persist data dict to JSON file."""
    _ensure_data_dir()
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)