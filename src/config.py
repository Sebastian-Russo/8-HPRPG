import os
from dotenv import load_dotenv

load_dotenv()

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Haiku for fast, cheap decisions
CLAUDE_MODEL_FAST  = "claude-haiku-4-5-20251001"

# Sonnet for narrative generation — this is what the player reads
CLAUDE_MODEL_SMART = "claude-sonnet-4-6"

# Vector store — reuse the one built in project 7
# Point this at your agenti-rag vectorstore folder
VECTORSTORE_PATH = "../agenti-rag/vectorstore"
COLLECTION_NAME  = "hp_books"
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"

# Retrieval
LORE_TOP_K = 3   # chunks of lore to retrieve per action
             # fewer than RAG project because we want speed in a game

# Game settings
SAVES_DIR        = "saves"
SCENE_HISTORY_MAX = 10   # how many past scenes to keep in state
                          # prevents the prompt from growing forever
