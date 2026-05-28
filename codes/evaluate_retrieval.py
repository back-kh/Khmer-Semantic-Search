#!/usr/bin/env python3
#author: Nimol Thuon
"""
evaluate_retrieval.py

Simple retrieval evaluation script for KSE-Web-style datasets.

Expected files:
  documents.jsonl : one JSON object per document
    {"doc_id": "D0001", "title": "...", "text": "...", "category": "..."}

  queries.jsonl : one JSON object per query
    {"query_id": "Q0001", "query": "...", "query_type": "...", "category": "..."}

  qrels.tsv : tab-separated relevance labels
    query_id    doc_id    relevance
    Q0001       D0001     2
    Q0001       D0042     1
    Q0001       D0333     0

Relevance labels:
  2 = highly relevant
  1 = partially relevant
  0 = non-relevant

Supported methods:
  bm25   : character n-gram BM25
  dense  : multilingual sentence embedding retrieval using sentence-transformers
  hybrid : min-max score fusion of BM25 and dense scores

Example:
  python evaluate_retrieval.py \
    --documents data/documents.jsonl \
    --queries data/queries.jsonl \
    --qrels data/qrels.tsv \
    --method bm25 \
    --output_dir results/bm25

Dense/hybrid require:
  pip install sentence-transformers torch
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np


# -----------------------------
# Loading utilities
# -----------------------------


def read_jsonl(path: str) -> List[dict]:
    rows: List[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_no} in {path}: {exc}") from exc
    return rows


def get_first(row: dict, keys: Iterable[str], default: str = "") -> str:
    for key in keys:
        value = row.get(key)
        if value is not None:
            return str(value)
    return default


def load_documents(path: str) -> Tuple[List[str], List[str]]:
    rows = read_jsonl(path)
    doc_ids: List[str] = []
    doc_texts: List[str] = []
    seen = set()

    for i, row in enumerate(rows):
        doc_id = get_first(row, ["doc_id", "id", "document_id"], default=f"D{i:06d}")
        if doc_id in seen:
            raise ValueError(f"Duplicate doc_id found: {doc_id}")
        seen.add(doc_id)

        title = get_first(row, ["title", "doc_title"], default="")
        body = get_first(row, ["text", "body", "content", "contents", "cleaned_text"], default="")
        text = (title + "\n" + body).strip()
        doc_ids.append(doc_id)
        doc_texts.append(text)

    if not doc_ids:
        raise ValueError(f"No documents loaded from {path}")
    return doc_ids, doc_texts


def load_queries(path: str) -> Tuple[List[str], List[str]]:
    rows = read_jsonl(path)
    query_ids: List[str] = []
    queries: List[str] = []
    seen = set()

    for i, row in enumerate(rows):
        query_id = get_first(row, ["query_id", "qid", "id"], default=f"Q{i:06d}")
        if query_id in seen:
            raise ValueError(f"Duplicate query_id found: {query_id}")
        seen.add(query_id)

        query = get_first(row, ["query", "text", "question"], default="")
        query_ids.append(query_id)
        queries.append(query)

    if not query_ids:
        raise ValueError(f"No queries loaded from {path}")
    return query_ids, queries


def load_qrels(path: str) -> Dict[str, Dict[str, int]]:
    """Load qrels from TSV with or without header."""
    qrels: Dict[str, Dict[str, int]] = defaultdict(dict)

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for line_no, row in enumerate(reader, start=1):
            if not row or all(not c.strip() for c in row):
                continue
            if len(row) < 3:
                raise ValueError(f"qrels.tsv line {line_no} must have at least 3 columns")

            qid, did, rel_str = row[0].strip(), row[1].strip(), row[2].strip()
            if line_no == 1 and qid.lower() in {"query_id", "qid"}:
                continue

            try:
                rel = int(float(rel_str))
            except ValueError as exc:
                raise ValueError(f"Invalid relevance value on line {line_no}: {rel_str}") from exc

            qrels[qid][did] = rel

    if not qrels:
        raise ValueError(f"No qrels loaded from {path}")
    return dict(qrels)


# -----------------------------
# Character n-gram BM25
# -----------------------------


def normalize_khmer_text(text: str) -> str:
    """Light normalization for character n-gram retrieval."""
    text = text.strip()
    text = re.sub(r"\s+", "", text)
    return text


def char_ngrams(text: str, n_values: Tuple[int, ...] = (2, 3, 4)) -> List[str]:
    text = normalize_khmer_text(text)
    if not text:
        return []

    grams: List[str] = []
    length = len(text)
    for n in n_values:
        if length >= n:
            grams.extend(text[i : i + n] for i in range(length - n + 1))
    return grams


@dataclass
class BM25Index:
    doc_ids: List[str]
    tokenized_docs: List[List[str]]
    k1: float = 1.2
    b: float = 0.75

    def __post_init__(self) -> None:
        self.n_docs = len(self.tokenized_docs)
        self.doc_lens = np.array([len(x) for x in self.tokenized_docs], dtype=np.float32)
        self.avgdl = float(np.mean(self.doc_lens)) if self.n_docs else 0.0

        self.inverted: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
        df: Counter[str] = Counter()

        for doc_idx, tokens in enumerate(self.tokenized_docs):
            tf = Counter(tokens)
            for token, count in tf.items():
                self.inverted[token].append((doc_idx, count))
                df[token] += 1

        self.idf: Dict[str, float] = {}
        for token, freq in df.items():
            # BM25+ style positive idf variant
            self.idf[token] = math.log(1.0 + (self.n_docs - freq + 0.5) / (freq + 0.5))

    def score(self, query_tokens: List[str]) -> np.ndarray:
        scores = np.zeros(self.n_docs, dtype=np.float32)
        if not query_tokens:
            return scores

        # Use unique query terms for standard BM25 scoring.
        for token in set(query_tokens):
            postings = self.inverted.get(token)
            if not postings:
                continue
            idf = self.idf.get(token, 0.0)
            for doc_idx, tf in postings:
                dl = self.doc_lens[doc_idx]
                denom = tf + self.k1 * (1.0 - self.b + self.b * dl / max(self.avgdl, 1e-9))
                scores[doc_idx] += idf * (tf * (self.k1 + 1.0)) / denom
        return scores


def build_bm25(doc_ids: List[str], doc_texts: List[str]) -> BM25Index:
    tokenized_docs = [char_ngrams(text) for text in doc_texts]
    return BM25Index(doc_ids=doc_ids, tokenized_docs=tokenized_docs)


# -----------------------------
# Dense retrieval
# -----------------------------


def dense_encode(
    texts: List[str],
    model_name: str,
    batch_size: int,
    prefix: str,
) -> np.ndarray:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ImportError(
            "Dense and hybrid retrieval require sentence-transformers. "
            "Install it with: pip install sentence-transformers torch"
        ) from exc

    model = SentenceTransformer(model_name)
    prefixed = [prefix + t for t in texts]
    emb = model.encode(
        prefixed,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return emb.astype(np.float32)


# -----------------------------
# Metrics
# -----------------------------


def dcg_at_k(labels: List[int], k: int) -> float:
    labels = labels[:k]
    score = 0.0
    for i, rel in enumerate(labels, start=1):
        score += (2**rel - 1) / math.log2(i + 1)
    return score


def evaluate_run(
    run: Dict[str, List[Tuple[str, float]]],
    qrels: Dict[str, Dict[str, int]],
    cutoffs: Tuple[int, ...] = (5, 10),
) -> Dict[str, float]:
    per_metric: Dict[str, List[float]] = defaultdict(list)

    for qid, rels in qrels.items():
        ranked = run.get(qid, [])
        relevant_docs = {did for did, rel in rels.items() if rel > 0}
        if not relevant_docs:
            continue

        ranked_doc_ids = [did for did, _score in ranked]

        for k in cutoffs:
            top_k = ranked_doc_ids[:k]
            hits = [1 if did in relevant_docs else 0 for did in top_k]
            num_hits = sum(hits)

            recall = num_hits / len(relevant_docs)
            precision = num_hits / k

            mrr = 0.0
            for rank, did in enumerate(top_k, start=1):
                if did in relevant_docs:
                    mrr = 1.0 / rank
                    break

            graded_labels = [rels.get(did, 0) for did in top_k]
            ideal_labels = sorted(rels.values(), reverse=True)
            dcg = dcg_at_k(graded_labels, k)
            idcg = dcg_at_k(ideal_labels, k)
            ndcg = dcg / idcg if idcg > 0 else 0.0

            per_metric[f"Recall@{k}"].append(recall)
            per_metric[f"Precision@{k}"].append(precision)
            per_metric[f"MRR@{k}"].append(mrr)
            per_metric[f"nDCG@{k}"].append(ndcg)

    return {name: float(np.mean(values)) if values else 0.0 for name, values in per_metric.items()}


# -----------------------------
# Ranking helpers
# -----------------------------


def minmax(scores: np.ndarray) -> np.ndarray:
    min_s = float(np.min(scores))
    max_s = float(np.max(scores))
    if abs(max_s - min_s) < 1e-12:
        return np.zeros_like(scores, dtype=np.float32)
    return ((scores - min_s) / (max_s - min_s)).astype(np.float32)


def top_docs(doc_ids: List[str], scores: np.ndarray, top_k: int) -> List[Tuple[str, float]]:
    if len(scores) == 0:
        return []
    top_k = min(top_k, len(scores))
    # Full sort is fine for 3K documents and keeps deterministic order.
    order = np.argsort(-scores, kind="mergesort")[:top_k]
    return [(doc_ids[i], float(scores[i])) for i in order]


def write_outputs(
    output_dir: str,
    method: str,
    run: Dict[str, List[Tuple[str, float]]],
    metrics: Dict[str, float],
) -> None:
    os.makedirs(output_dir, exist_ok=True)

    metrics_path = os.path.join(output_dir, f"metrics_{method}.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    run_path = os.path.join(output_dir, f"run_{method}.tsv")
    with open(run_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["query_id", "doc_id", "rank", "score", "method"])
        for qid, ranked in run.items():
            for rank, (doc_id, score) in enumerate(ranked, start=1):
                writer.writerow([qid, doc_id, rank, f"{score:.8f}", method])

    print(f"Saved metrics to: {metrics_path}")
    print(f"Saved run file to: {run_path}")


# -----------------------------
# Main
# -----------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate BM25, dense, or hybrid retrieval on KSE-Web.")
    parser.add_argument("--documents", required=True, help="Path to documents.jsonl")
    parser.add_argument("--queries", required=True, help="Path to queries.jsonl")
    parser.add_argument("--qrels", required=True, help="Path to qrels.tsv")
    parser.add_argument("--method", choices=["bm25", "dense", "hybrid"], default="bm25")
    parser.add_argument("--model_name", default="intfloat/multilingual-e5-small", help="SentenceTransformer model for dense/hybrid retrieval")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size for dense encoding")
    parser.add_argument("--fusion_alpha", type=float, default=0.5, help="Hybrid fusion weight for BM25; dense weight is 1-alpha")
    parser.add_argument("--top_k", type=int, default=20, help="Number of documents to retrieve per query")
    parser.add_argument("--output_dir", default="results", help="Directory for metrics and run output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("Loading dataset...")
    doc_ids, doc_texts = load_documents(args.documents)
    query_ids, queries = load_queries(args.queries)
    qrels = load_qrels(args.qrels)

    print(f"Documents: {len(doc_ids)}")
    print(f"Queries:   {len(query_ids)}")
    print(f"Qrels:     {sum(len(v) for v in qrels.values())} query-document labels")

    bm25_index = None
    doc_emb = None
    query_emb = None

    if args.method in {"bm25", "hybrid"}:
        print("Building character n-gram BM25 index...")
        bm25_index = build_bm25(doc_ids, doc_texts)

    if args.method in {"dense", "hybrid"}:
        print(f"Encoding documents with {args.model_name}...")
        doc_emb = dense_encode(doc_texts, args.model_name, args.batch_size, prefix="passage: ")
        print(f"Encoding queries with {args.model_name}...")
        query_emb = dense_encode(queries, args.model_name, args.batch_size, prefix="query: ")

    run: Dict[str, List[Tuple[str, float]]] = {}

    print(f"Running retrieval method: {args.method}")
    for qi, (qid, query) in enumerate(zip(query_ids, queries)):
        if args.method == "bm25":
            assert bm25_index is not None
            scores = bm25_index.score(char_ngrams(query))

        elif args.method == "dense":
            assert doc_emb is not None and query_emb is not None
            scores = doc_emb @ query_emb[qi]

        else:  # hybrid
            assert bm25_index is not None
            assert doc_emb is not None and query_emb is not None
            bm25_scores = bm25_index.score(char_ngrams(query))
            dense_scores = doc_emb @ query_emb[qi]
            scores = args.fusion_alpha * minmax(bm25_scores) + (1.0 - args.fusion_alpha) * minmax(dense_scores)

        run[qid] = top_docs(doc_ids, scores, args.top_k)

    metrics = evaluate_run(run, qrels, cutoffs=(5, 10))

    print("\nEvaluation results")
    print("------------------")
    for name in ["Recall@5", "Precision@5", "MRR@5", "nDCG@5", "Recall@10", "Precision@10", "MRR@10", "nDCG@10"]:
        print(f"{name:12s}: {metrics.get(name, 0.0):.4f}")

    write_outputs(args.output_dir, args.method, run, metrics)


if __name__ == "__main__":
    main()
