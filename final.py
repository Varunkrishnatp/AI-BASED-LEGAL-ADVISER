import json
import faiss
import numpy as np
import os
import re
from sentence_transformers import SentenceTransformer

# =========================
# AUTO PATH
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAG_JSON_PATH = os.path.join(BASE_DIR, "dddd.json")

if not os.path.exists(RAG_JSON_PATH):
    raise FileNotFoundError(f"❌ JSON not found: {RAG_JSON_PATH}")

# =========================
# LOAD JSON
# =========================
with open(RAG_JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

corpus = []
punishments = []
sections = []

for entry in data:
    raw_sec = str(entry.get("Section"))
    sec = re.sub(r'\D', '', raw_sec)

    title = entry.get("Title", "")
    txt = entry.get("FullText", "").strip()

    # ✅ Extract punishment if embedded
    pun = entry.get("punishment")
    if not pun or pun == "null":
        match = re.search(r'punishment:\s*(.*)', txt.lower())
        if match:
            pun = match.group(1)
        else:
            pun = "Not specified"

    # ✅ Clean text
    txt = re.sub(r'punishment:.*', '', txt, flags=re.IGNORECASE)

    # ✅ Add section + title
    combined = f"Section {sec} — {title}\n{txt}"

    corpus.append(combined)
    punishments.append(pun)
    sections.append(sec)

print("✅ Sections Loaded:", sections[:20])

# =========================
# EMBEDDING
# =========================
embedder = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embedder.encode(corpus, convert_to_numpy=True)

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

print("✅ FAISS READY")

# =========================
# DETECT SECTION
# =========================
def detect_section(question):
    match = re.search(r'(section\s*)?(\d+)', question.lower())
    return match.group(2) if match else None

# =========================
# FORMAT OUTPUT
# =========================
def format_output(text, punishment):
    return f"""
### ✅ Applicable Law
{text}

### ⚖️ Punishment
{punishment}

### 📖 Explanation
This section explains the offence and its legal consequences in simple terms.
"""

# =========================
# KEYWORD ROUTER (IMPORTANT FIX)
# =========================
def keyword_router(question):
    q = question.lower()

    # ✅ Theft
    if "theft" in q:
        for i, text in enumerate(corpus):
            if "theft" in text.lower() and "preparation" not in text.lower():
                return i

    # Add more rules if needed
    return None

# =========================
# MAIN FUNCTION
# =========================
def ask_legal_ai(question):

    sec = detect_section(question)
    print("🔍 Detected:", sec)

    # ✅ STRICT SECTION MATCH
    if sec:
        if sec in sections:
            i = sections.index(sec)
            return format_output(corpus[i], punishments[i])
        else:
            return f"❌ Section {sec} not found in dataset."

    # ✅ KEYWORD ROUTING
    route_idx = keyword_router(question)
    if route_idx is not None:
        return format_output(corpus[route_idx], punishments[route_idx])

    # ✅ FAISS (LAST OPTION)
    q_vec = embedder.encode([question])
    _, I = index.search(q_vec, 1)

    idx = I[0][0]
    return format_output(corpus[idx], punishments[idx])