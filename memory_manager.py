# memory_manager.py

import json
import os

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memories):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, indent=4)

def add_memory(text):
    memories = load_memory()
    memories.append(text)
    save_memory(memories)

def search_memory(query):
    query = query.lower()
    return [m for m in load_memory() if any(word in m.lower() for word in query.split())]
