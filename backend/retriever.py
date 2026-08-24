"""
RAG retriever — loads the TF-IDF index built by build_index.py and
returns the top-k most relevant corpus records for a query.

No network calls. Runs entirely from local files.
"""
import json, os, pickle
import numpy as np
import scipy.sparse
from sklearn.metrics.pairwise import cosine_similarity

INDEX_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus", "index")


class TFIDFRetriever:
    def __init__(self, index_dir: str = INDEX_DIR):
        index_dir = os.path.abspath(index_dir)
        self.vectorizer = pickle.load(
            open(os.path.join(index_dir, "tfidf_vectorizer.pkl"), "rb")
        )
        self.matrix = scipy.sparse.load_npz(
            os.path.join(index_dir, "tfidf_matrix.npz")
        )
        self.records = json.load(
            open(os.path.join(index_dir, "records.json"), encoding="utf-8")
        )

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Return top_k records most relevant to query, with a score field."""
        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self.matrix).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            rec = dict(self.records[idx])
            rec["retrieval_score"] = float(scores[idx])
            results.append(rec)
        return results
