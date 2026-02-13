import json
from pathlib import Path


def load_config() -> dict:
    """Load test_config.json from the same directory as this module."""
    config_path = Path(__file__).parent / "test_config.json"
    with open(config_path) as f:
        return json.load(f)
