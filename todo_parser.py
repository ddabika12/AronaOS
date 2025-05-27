# todo_parser.py
import spacy
import dateparser
from dateparser.search import search_dates
from datetime import datetime
import os
import dateparser.data.date_translation_data.en

model_path = os.path.join(os.path.dirname(__file__), "en_core_web_sm")
nlp = spacy.load(model_path)

import re

def parse_todo_with_deadline(sentence: str):
    original_sentence = sentence.strip()
    doc = nlp(original_sentence)

    subject_like = {"i", "you", "we", "he", "she", "they"}
    is_verb_start = len(doc) > 0 and doc[0].pos_ == "VERB"
    has_no_subject = not any(token.dep_ == "nsubj" and token.text.lower() in subject_like for token in doc)
    has_checkbox = original_sentence.startswith(("- [ ]", "*", "-"))
    is_todo = (is_verb_start and has_no_subject) or has_checkbox

    dp_settings = {
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': datetime.now()
    }

    found = search_dates(original_sentence, settings=dp_settings)
    deadline_dt = None
    deadline_text = None

    # Reject clearly bad matches like "see"
    if found:
        filtered = []
        for text, parsed in found:
            if len(text) > 3 and parsed > datetime.now():  # Avoid tiny false matches like "see"
                filtered.append((text, parsed))
        if filtered:
            deadline_text, deadline_dt = filtered[0]

    # Fallback to manual search for "before 5pm", etc.
    if not deadline_dt:
        match = re.search(r'(before|by|at|on|around)\s+([^\.,!?]+)', original_sentence, re.IGNORECASE)
        if match:
            phrase = match.group(0)
            parsed = dateparser.parse(phrase, settings=dp_settings)
            if parsed and parsed > datetime.now():
                deadline_text = phrase
                deadline_dt = parsed

    # Strip out the date phrase and trailing words like "morning"/"evening"
    task_name = original_sentence
    if deadline_text:
        cleanup_pattern = r'\b(' + re.escape(deadline_text) + r')\b(\s+(morning|evening|night|afternoon))?'
        task_name = re.sub(cleanup_pattern, '', task_name, flags=re.IGNORECASE).strip(",. ")

    task_name = task_name.title()

    return {
        "is_todo": is_todo,
        "deadline": deadline_dt,
        "task_name": task_name
    }



