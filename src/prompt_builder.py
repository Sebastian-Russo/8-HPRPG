"""
Think of this like a director's briefing packet given to an actor before a scene.
The actor needs to know: who they're playing, what's happened so far,
what the world looks like right now, and what just happened on stage.

This file assembles all of that into one structured prompt so Claude
has everything it needs to generate the next scene consistently.
"""

import json
from src.config import CLAUDE_MODEL_SMART


def build_game_prompt(state: dict, player_action: str, lore_passages: list[str]) -> str:
    """
    Assemble the full prompt Claude receives for each player action.

    It has 5 sections:
      1. Role        — what Claude is
      2. World       — retrieved lore passages
      3. Character   — the player's current state
      4. History     — last N scenes for continuity
      5. Action      — what the player just did
    """

    # ── Section 1: Role ───────────────────────────────────────
    role = """You are the narrator of an interactive Harry Potter RPG.
You generate immersive, canon-accurate scenes based on the player's actions.
You must stay true to the HP world — its rules, characters, and tone.
Keep responses to 3-4 paragraphs. End every scene with 2-3 possible actions
the player could take next, formatted as a numbered list."""

    # ── Section 2: Lore ───────────────────────────────────────
    if lore_passages:
        lore_text = "\n\n".join(f"- {p}" for p in lore_passages)
        lore = f"RELEVANT LORE FROM THE BOOKS:\n{lore_text}"
    else:
        lore = "RELEVANT LORE: None retrieved for this action."

    # ── Section 3: Character ──────────────────────────────────
    character = f"""PLAYER CHARACTER:
- Name: {state['player_name']}
- House: {state['house'] or 'not yet sorted'}
- Year: {state['year']}
- Location: {state['current_location']}
- Health: {state['health']}/100
- Spells known: {', '.join(state['spells_learned']) or 'none yet'}
- Inventory: {', '.join(state['inventory']) or 'nothing'}
- Relationships: {json.dumps(state['relationships']) or 'none established'}"""

    # ── Section 4: History ────────────────────────────────────
    if state["scene_history"]:
        history_text = "\n\n".join(state["scene_history"][-3:])  # last 3 scenes
        history = f"RECENT SCENE HISTORY:\n{history_text}"
    else:
        history = "RECENT SCENE HISTORY: This is the beginning of the adventure."

    # ── Section 5: Action + state update instruction ──────────
    action = f"""PLAYER ACTION: {player_action}

Generate the next scene. Then on a new line write EXACTLY this separator:
---STATE_UPDATE---
Followed by a JSON object of ONLY the fields that changed. Example:
{{"current_location": "Potions classroom", "spells_learned": ["Wingardium Leviosa"]}}
If nothing changed, write: {{}}"""

    return "\n\n".join([role, lore, character, history, action])


def parse_response(raw: str) -> tuple[str, dict]:
    """
    Split Claude's response into narrative text and state updates.

    Claude returns:
      [narrative scene]
      ---STATE_UPDATE---
      {"key": "value"}

    We split on the separator and parse the JSON half.
    """
    separator = "---STATE_UPDATE---"

    if separator in raw:
        parts     = raw.split(separator, 1)
        narrative = parts[0].strip()
        try:
            updates = json.loads(parts[1].strip())
        except json.JSONDecodeError:
            updates = {}
    else:
        # If Claude forgot the separator, just take the whole thing as narrative
        narrative = raw.strip()
        updates   = {}

    return narrative, updates
