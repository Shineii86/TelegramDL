import os
import json

CHECKPOINT_FILE = "checkpoint.json"


def load_checkpoint():
    """Load checkpoint data."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {"downloaded": [], "failed": [], "stats": {"downloaded": 0, "skipped": 0, "failed": 0}}


def save_checkpoint(data):
    """Save checkpoint data."""
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f)


def clear_checkpoint():
    """Clear checkpoint data."""
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
