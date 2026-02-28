"""
Think of this like a TV show's writers room.
The writers know the characters, the world, and what just happened —
they take the latest plot development and decide what happens next.

This file coordinates everything: loads the player's state, retrieves
relevant lore, builds the prompt, calls Claude, parses the response,
and saves the updated state. It's the orchestrator — like rag_pipeline.py
was in project 7, but for a game loop instead of a one-shot question.
"""

import anthropic

from src.config        import ANTHROPIC_API_KEY, CLAUDE_MODEL_SMART, SCENE_HISTORY_MAX
from src.state_manager import load_state, update_state, append_scene
from src.lore_retriever import LoreRetriever
from src.prompt_builder import build_game_prompt, parse_response


class GameEngine:
    def __init__(self):
        self.client   = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.retriever = LoreRetriever()
        print("[GameEngine] Ready.")

    def start_game(self, player_name: str, house: str) -> dict:
        """
        Initialize a new player or load an existing one.
        Returns the opening scene.
        """
        state = load_state(player_name)

        # If this is a new player, set their house
        if not state["house"] and house:
            state["house"] = house
            from src.state_manager import save_state
            save_state(state)

        # Generate the opening scene if no history yet
        if not state["scene_history"]:
            opening_action = "I arrive at Hogwarts for the first time, ready to begin my adventure."
            return self.take_action(player_name, opening_action)

        # Returning player — show last scene
        return {
            "narrative":        state["scene_history"][-1],
            "state":            state,
            "returning_player": True
        }

    def take_action(self, player_name: str, action: str) -> dict:
        """
        The core game loop — one full turn.

        1. Load current state
        2. Retrieve relevant lore for this action
        3. Build the prompt
        4. Call Claude
        5. Parse narrative + state updates
        6. Save updated state
        7. Return narrative to the player
        """
        # Step 1: load state
        state = load_state(player_name)

        # Step 2: retrieve lore
        # Search query combines location + action for better relevance
        lore_query   = f"{state['current_location']} {action}"
        lore_passages = self.retriever.retrieve(lore_query)

        # Step 3: build prompt
        prompt = build_game_prompt(state, action, lore_passages)

        # Step 4: call Claude
        response = self.client.messages.create(
            model      = CLAUDE_MODEL_SMART,
            max_tokens = 1000,
            messages   = [{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text

        # Step 5: parse response
        narrative, updates = parse_response(raw)

        # Step 6: apply state updates and append scene to history
        if updates:
            state = update_state(state, updates)
        state = append_scene(state, narrative, SCENE_HISTORY_MAX)

        # Step 7: return to player
        return {
            "narrative": narrative,
            "state":     state,
            "lore_used": len(lore_passages)
        }
