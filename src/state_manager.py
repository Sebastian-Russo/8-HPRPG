"""
Think of this like a save file in a video game.
When you quit and reload, the game reads the save file and puts you
exactly where you left off — same health, same inventory, same location.

This file handles reading and writing that save file.
Every player gets their own JSON file in the saves/ folder.
"""

import os
import json
from src.config import SAVES_DIR


# Default state for a brand new player
DEFAULT_STATE = {
    "player_name":       "",
    "house":             "",
    "year":              1,
    "spells_learned":    ["Lumos"],
    "inventory":         ["wand", "Hogwarts letter"],
    "relationships":     {},
    "current_location":  "Hogwarts Express",
    "scene_history":     [],
    "health":            100
}


def _save_path(player_name: str) -> str:
    """Build the file path for a player's save file."""
    safe_name = player_name.lower().replace(" ", "_")
    return os.path.join(SAVES_DIR, f"{safe_name}.json")


def load_state(player_name: str) -> dict:
    """
    Load a player's state from disk.
    If no save file exists, create a fresh default state.
    """
    os.makedirs(SAVES_DIR, exist_ok=True)
    path = _save_path(player_name)

    if not os.path.exists(path):
        state = DEFAULT_STATE.copy()
        state["player_name"] = player_name
        save_state(state)
        return state

    with open(path, "r") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    """Write a player's state to disk."""
    os.makedirs(SAVES_DIR, exist_ok=True)
    path = _save_path(state["player_name"])
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def update_state(state: dict, updates: dict) -> dict:
    """
    Merge updates into the current state and save.

    Claude returns a JSON object of what changed after each action —
    e.g. a new spell learned, location changed, item added.
    This function applies those changes cleanly.
    """
    for key, value in updates.items():
        if key == "spells_learned" and isinstance(value, list):
            # Append new spells rather than replacing the whole list
            existing = state.get("spells_learned", [])
            state["spells_learned"] = list(set(existing + value))
        elif key == "inventory" and isinstance(value, list):
            # Same for inventory
            existing = state.get("inventory", [])
            state["inventory"] = list(set(existing + value))
        elif key == "relationships" and isinstance(value, dict):
            # Merge relationship updates
            state["relationships"].update(value)
        else:
            state[key] = value

    save_state(state)
    return state


def append_scene(state: dict, scene_text: str, max_history: int) -> dict:
    """
    Add a new scene to history and trim if over the limit.
    Oldest scenes are dropped first — like a sliding window.
    """
    state["scene_history"].append(scene_text)
    if len(state["scene_history"]) > max_history:
        state["scene_history"] = state["scene_history"][-max_history:]
    save_state(state)
    return state
