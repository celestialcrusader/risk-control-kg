"""
Hybrid Candidate Retriever: Dense Neural Vectors + BM25 Lexical Keyword Search (STORY-COMP-203).

Combines dense semantic embeddings with BM25 Okapi lexical scoring using Reciprocal
Rank Fusion (RRF) to guarantee high recall for short regulatory queries and domain acronyms (e.g. MFA, SoD, SLA).
"""
import re
import numpy as np
from rank_bm25 import BM25Okapi
from typing import List, Tuple, Dict, Any, Callable


class HybridCandidateRetriever:
    """Hybrid Search combining Dense Neural Embeddings with BM25 Lexical Matching."""

    def __init__(self, controls: List[Any], embedder_fn: Callable[[List[str]], np.ndarray]):
        self.controls = controls
        self.embedder_fn = embedder_fn

        # 1. Build Tokenized Corpus for BM25
        self.corpus = [self._tokenize(c) for c in controls]
        self.bm25 = BM25Okapi(self.corpus)

        # 2. Build Dense Vectors for Controls
        dense_texts = [
            f"{c.framework_obj_id} {getattr(c, 'objective_name', '')}: {getattr(c, 'objective_text', '')[:400]}"
            for c in controls
        ]
        self.control_vectors = self.embedder_fn(dense_texts)

    def _tokenize(self, control: Any) -> List[str]:
        """Tokenizes control ID, title, and body for BM25 index."""
        cid = getattr(control, "framework_obj_id", "") or ""
        name = getattr(control, "objective_name", "") or ""
        text = getattr(control, "objective_text", "") or ""
        combined = f"{cid} {name} {text}".lower()
        # Clean punctuation and tokenize
        words = re.findall(r"\b[a-zA-Z0-9_-]+\b", combined)
        return words

    def retrieve_top_k_decompounded(self, sub_queries: List[str], sub_vectors: np.ndarray, top_k: int = 15) -> List[Tuple[Any, float, str]]:
        """Retrieves top_k controls aggregating RRF across decompounded sub-queries."""
        if not self.controls or not sub_queries:
            return []

        k = 60
        combined_rrf: Dict[int, float] = {}
        best_dense_sims: Dict[int, float] = {}

        for i, q_text in enumerate(sub_queries):
            q_vec = sub_vectors[i]
            q_tokens = re.findall(r"\b[a-zA-Z0-9_-]+\b", q_text.lower())
            bm25_scores = self.bm25.get_scores(q_tokens) if q_tokens else np.zeros(len(self.controls))
            bm25_ranks = np.argsort(bm25_scores)[::-1]

            q_norm = np.linalg.norm(q_vec)
            q_vec_norm = q_vec / q_norm if q_norm > 0 else q_vec
            dense_scores = np.dot(self.control_vectors, q_vec_norm)
            dense_ranks = np.argsort(dense_scores)[::-1]

            pool_depth = min(50, len(self.controls))
            for rank in range(pool_depth):
                b_idx = int(bm25_ranks[rank])
                if bm25_scores[b_idx] > 0.0:
                    combined_rrf[b_idx] = combined_rrf.get(b_idx, 0.0) + (1.5 / (k + rank + 1))

                d_idx = int(dense_ranks[rank])
                combined_rrf[d_idx] = combined_rrf.get(d_idx, 0.0) + (1.0 / (k + rank + 1))
                best_dense_sims[d_idx] = max(best_dense_sims.get(d_idx, 0.0), float(dense_scores[d_idx]))

        sorted_indices = sorted(combined_rrf.keys(), key=lambda i: combined_rrf[i], reverse=True)[:top_k]

        results = []
        for idx in sorted_indices:
            ctrl = self.controls[idx]
            sim = best_dense_sims.get(idx, 0.50)
            explanation = f"Multi-Intent RRF: {combined_rrf[idx]:.4f} (Max Dense Sim: {sim:.2f})"
            results.append((ctrl, sim, explanation))

        return results

    def retrieve_top_k_with_vector(self, query_text: str, q_vec: np.ndarray, top_k: int = 15) -> List[Tuple[Any, float, str]]:
        """Retrieves top_k controls using precomputed query vector and BM25."""
        if not self.controls:
            return []

        # 1. BM25 Lexical Scoring
        q_tokens = re.findall(r"\b[a-zA-Z0-9_-]+\b", query_text.lower())
        bm25_scores = self.bm25.get_scores(q_tokens) if q_tokens else np.zeros(len(self.controls))
        bm25_ranks = np.argsort(bm25_scores)[::-1]

        # 2. Dense Vector Scoring
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec_norm = q_vec / q_norm
        else:
            q_vec_norm = q_vec

        dense_scores = np.dot(self.control_vectors, q_vec_norm)
        dense_ranks = np.argsort(dense_scores)[::-1]

        # 3. Reciprocal Rank Fusion (RRF)
        k = 60
        rrf_scores: Dict[int, float] = {}
        pool_depth = min(50, len(self.controls))
        for rank in range(pool_depth):
            b_idx = int(bm25_ranks[rank])
            if bm25_scores[b_idx] > 0.0:
                rrf_scores[b_idx] = rrf_scores.get(b_idx, 0.0) + (1.5 / (k + rank + 1))
            
            d_idx = int(dense_ranks[rank])
            rrf_scores[d_idx] = rrf_scores.get(d_idx, 0.0) + (1.0 / (k + rank + 1))

        sorted_indices = sorted(rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True)[:top_k]

        results = []
        for idx in sorted_indices:
            ctrl = self.controls[idx]
            sim = float(dense_scores[idx])
            explanation = f"RRF: {rrf_scores[idx]:.4f} (Dense Sim: {sim:.2f}, BM25: {bm25_scores[idx]:.2f})"
            results.append((ctrl, sim, explanation))

        return results

    def retrieve_top_k(self, query_text: str, top_k: int = 15) -> List[Tuple[Any, float, str]]:
        """
        Retrieves top_k controls using Reciprocal Rank Fusion between BM25 and Dense Cosine similarity.
        Returns List of (control, dense_similarity, score_explanation).
        """
        if not self.controls:
            return []

        # 1. BM25 Lexical Scoring
        q_tokens = re.findall(r"\b[a-zA-Z0-9_-]+\b", query_text.lower())
        bm25_scores = self.bm25.get_scores(q_tokens) if q_tokens else np.zeros(len(self.controls))
        bm25_ranks = np.argsort(bm25_scores)[::-1]

        # 2. Dense Vector Scoring
        q_vec = self.embedder_fn([query_text])[0]
        # Normalize if not normalized
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        dense_scores = np.dot(self.control_vectors, q_vec)
        dense_ranks = np.argsort(dense_scores)[::-1]

        # 3. Reciprocal Rank Fusion (RRF)
        # RRF formula: Score = sum(1 / (k + rank))
        k = 60
        rrf_scores: Dict[int, float] = {}
        
        # Consider candidates with non-zero BM25 or high dense similarity
        pool_depth = min(50, len(self.controls))
        for rank in range(pool_depth):
            # BM25 rank - only reward if there is an actual keyword hit
            b_idx = int(bm25_ranks[rank])
            if bm25_scores[b_idx] > 0.0:
                rrf_scores[b_idx] = rrf_scores.get(b_idx, 0.0) + (1.5 / (k + rank + 1))
            
            # Dense rank
            d_idx = int(dense_ranks[rank])
            rrf_scores[d_idx] = rrf_scores.get(d_idx, 0.0) + (1.0 / (k + rank + 1))

        # Sort combined candidate indices
        sorted_indices = sorted(rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True)[:top_k]

        results = []
        for idx in sorted_indices:
            ctrl = self.controls[idx]
            sim = float(dense_scores[idx])
            explanation = f"RRF: {rrf_scores[idx]:.4f} (Dense Sim: {sim:.2f}, BM25: {bm25_scores[idx]:.2f})"
            results.append((ctrl, sim, explanation))

        return results
