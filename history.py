"""
history.py
Handles saving, loading, and clearing calculation history to a JSON file.
"""

import json
import os


class HistoryManager:
    def __init__(self):
        self.folder = "data"
        self.file = os.path.join(self.folder, "history.json")

        os.makedirs(self.folder, exist_ok=True)

        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                json.dump([], f)

    def save(self, expression, result):
        history = self.load()

        history.append({
            "expression": expression,
            "result": result
        })

        # Keep history from growing unbounded
        history = history[-200:]

        with open(self.file, "w") as f:
            json.dump(history, f, indent=4)

    def load(self):
        if not os.path.exists(self.file):
            return []

        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []

    def clear(self):
        with open(self.file, "w") as f:
            json.dump([], f)
