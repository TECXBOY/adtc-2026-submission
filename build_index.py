#!/usr/bin/env python3
"""
Builds a local TF-IDF retrieval index over corpus/wassce_bece_questions.jsonl.

Uses scikit-learn TfidfVectorizer + cosine similarity — zero network calls,
works offline on any Python 3.8+ with scikit-learn installed.

For 50 documents this retrieves accurately and is faster to load than a
sentence-transformer model (~5ms vs ~10s cold start).

Outputs:
  corpus/index/tfidf_matrix.npz   — sparse TF-IDF matrix
  corpus/index/tfidf_vocab.json   — vocabulary (for rebuild verification)
  corpus/index/records.json       — ordered list of records matching index rows
  corpus/index/index_type.txt     — "tfidf" (so RAG pipeline knows which loader)

Safe to re-run: overwrites outputs.
"""
import json, os, pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import scipy.sparse

CORPUS_PATH = "corpus/wassce_bece_questions.jsonl"
INDEX_DIR   = "corpus/index"

os.makedirs(INDEX_DIR, exist_ok=True)

records = [json.loads(l) for l in open(CORPUS_PATH, encoding="utf-8")]
print(f"Loaded {len(records)} records from {CORPUS_PATH}")

def record_to_text(r):
    """Concatenate all searchable fields into one string."""
    return (
        f"{r['subject']} {r['topic']} {r['exam']} "
        f"{r['question']} {r['solution']} {r['answer']}"
    )

texts = [record_to_text(r) for r in records]

# Fit TF-IDF
print("Fitting TF-IDF vectorizer…")
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),   # unigrams + bigrams
    max_features=8000,
    sublinear_tf=True,
)
tfidf_matrix = vectorizer.fit_transform(texts)
print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")

# Save
scipy.sparse.save_npz(f"{INDEX_DIR}/tfidf_matrix.npz", tfidf_matrix)
with open(f"{INDEX_DIR}/tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)
with open(f"{INDEX_DIR}/records.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
with open(f"{INDEX_DIR}/index_type.txt", "w") as f:
    f.write("tfidf\n")

print(f"Index saved to {INDEX_DIR}/")

# Quick self-test
print("\nRetrieval self-test (top-3 for 3 queries):")
test_queries = [
    "solve for x linear equation",
    "area of a circle radius",
    "Newton's law of motion",
]
for q in test_queries:
    q_vec = vectorizer.transform([q])
    scores = cosine_similarity(q_vec, tfidf_matrix).flatten()
    top_k = np.argsort(scores)[::-1][:3]
    print(f"\n  Query: '{q}'")
    for i, idx in enumerate(top_k):
        r = records[idx]
        print(f"    {i+1}. [{r['id']}] {r['subject']} / {r['topic']} (score={scores[idx]:.3f})")
        print(f"       Q: {r['question'][:80]}")
