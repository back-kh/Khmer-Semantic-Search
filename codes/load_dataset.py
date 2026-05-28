#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
load_dataset.py

Utility script for loading and validating the KSE-Web dataset.

Expected files:
  data/documents.jsonl
  data/queries.jsonl
  data/qrels.tsv

Example:
  python load_dataset.py --data_dir data

Optional Hugging Face export:
  pip install datasets
  python load_dataset.py --data_dir data --export_hf_dir kse_web_hf
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


Document = Dict[str, Any]
Query = Dict[str, Any]
Qrel = Dict[str, Any]


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Read a JSONL file into a list of dictionaries."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path} at line {line_no}: {exc}") from exc
            if not isinstance(item, dict):
                raise ValueError(f"Expected JSON object in {path} at line {line_no}")
            rows.append(item)
    return rows


def _normalize_qrel(row: Dict[str, Any], path: Path, row_no: int) -> Qrel:
    """Normalize and validate one qrel row."""
    qid = str(row.get("query_id", "")).strip()
    did = str(row.get("doc_id", "")).strip()
    rel_raw = str(row.get("relevance", "")).strip()

    if not qid or not did:
        raise ValueError(f"Missing query_id/doc_id in {path} at line {row_no}: {row}")

    try:
        rel = int(float(rel_raw))
    except ValueError as exc:
        raise ValueError(f"Invalid relevance value in {path} at line {row_no}: {rel_raw}") from exc

    if rel not in {0, 1, 2}:
        raise ValueError(
            f"Unexpected relevance value in {path} at line {row_no}: {rel}. Expected 0, 1, or 2."
        )

    return {"query_id": qid, "doc_id": did, "relevance": rel}


def read_qrels(path: Path) -> List[Qrel]:
    """
    Read qrels TSV.

    Supports both:
      query_id<TAB>doc_id<TAB>relevance
    and headerless TSV where the first three columns are query_id, doc_id, relevance.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    qrels: List[Qrel] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        first_line = f.readline()
        if not first_line:
            return []
        f.seek(0)

        has_header = "query_id" in first_line and "doc_id" in first_line
        if has_header:
            reader = csv.DictReader(f, delimiter="\t")
            required = {"query_id", "doc_id", "relevance"}
            if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
                raise ValueError(
                    f"qrels header must contain {sorted(required)}. Found: {reader.fieldnames}"
                )
            for row_no, row in enumerate(reader, start=2):
                qrels.append(_normalize_qrel(row, path, row_no))
        else:
            reader = csv.reader(f, delimiter="\t")
            for row_no, row in enumerate(reader, start=1):
                if not row or all(not x.strip() for x in row):
                    continue
                if len(row) < 3:
                    raise ValueError(f"Expected at least 3 TSV columns in {path} at line {row_no}: {row}")
                qrels.append(
                    _normalize_qrel(
                        {"query_id": row[0], "doc_id": row[1], "relevance": row[2]},
                        path,
                        row_no,
                    )
                )
    return qrels


def normalize_documents(documents: Iterable[Document]) -> List[Document]:
    """Ensure common document fields exist and are strings."""
    normalized: List[Document] = []
    for i, doc in enumerate(documents, start=1):
        doc_id = str(doc.get("doc_id") or doc.get("id") or f"D{i:06d}").strip()
        title = str(doc.get("title", "") or "").strip()
        text = str(doc.get("text") or doc.get("body") or doc.get("content") or "").strip()
        category = str(doc.get("category", "") or "").strip()
        source_url = str(doc.get("source_url") or doc.get("url") or "").strip()

        item = dict(doc)
        item.update({
            "doc_id": doc_id,
            "title": title,
            "text": text,
            "category": category,
            "source_url": source_url,
        })
        normalized.append(item)
    return normalized


def normalize_queries(queries: Iterable[Query]) -> List[Query]:
    """Ensure common query fields exist and are strings."""
    normalized: List[Query] = []
    for i, query in enumerate(queries, start=1):
        query_id = str(query.get("query_id") or query.get("id") or f"Q{i:04d}").strip()
        query_text = str(query.get("query") or query.get("text") or "").strip()
        query_type = str(query.get("query_type", "") or "").strip()
        category = str(query.get("category", "") or "").strip()
        source_doc_id = str(query.get("source_doc_id", "") or "").strip()

        item = dict(query)
        item.update({
            "query_id": query_id,
            "query": query_text,
            "query_type": query_type,
            "category": category,
            "source_doc_id": source_doc_id,
        })
        normalized.append(item)
    return normalized


def validate_dataset(documents: List[Document], queries: List[Query], qrels: List[Qrel]) -> None:
    """Validate IDs and qrels references."""
    doc_ids = [str(d["doc_id"]) for d in documents]
    query_ids = [str(q["query_id"]) for q in queries]

    duplicate_docs = [x for x, c in Counter(doc_ids).items() if c > 1]
    duplicate_queries = [x for x, c in Counter(query_ids).items() if c > 1]

    if duplicate_docs:
        raise ValueError(f"Duplicate doc_id values found. Examples: {duplicate_docs[:5]}")
    if duplicate_queries:
        raise ValueError(f"Duplicate query_id values found. Examples: {duplicate_queries[:5]}")

    doc_id_set = set(doc_ids)
    query_id_set = set(query_ids)
    missing_docs = sorted({row["doc_id"] for row in qrels if row["doc_id"] not in doc_id_set})
    missing_queries = sorted({row["query_id"] for row in qrels if row["query_id"] not in query_id_set})

    if missing_docs:
        raise ValueError(
            f"{len(missing_docs)} qrels doc_id values are missing from documents.jsonl. "
            f"Examples: {missing_docs[:5]}"
        )
    if missing_queries:
        raise ValueError(
            f"{len(missing_queries)} qrels query_id values are missing from queries.jsonl. "
            f"Examples: {missing_queries[:5]}"
        )


def load_kse_web(
    data_dir: str | Path | None = None,
    documents_path: str | Path | None = None,
    queries_path: str | Path | None = None,
    qrels_path: str | Path | None = None,
) -> Tuple[List[Document], List[Query], List[Qrel]]:
    """Load KSE-Web documents, queries, and qrels."""
    if data_dir is not None:
        base = Path(data_dir)
        documents_path = documents_path or base / "documents.jsonl"
        queries_path = queries_path or base / "queries.jsonl"
        qrels_path = qrels_path or base / "qrels.tsv"

    if documents_path is None or queries_path is None or qrels_path is None:
        raise ValueError("Provide either --data_dir or all of --documents, --queries, and --qrels.")

    documents = normalize_documents(read_jsonl(Path(documents_path)))
    queries = normalize_queries(read_jsonl(Path(queries_path)))
    qrels = read_qrels(Path(qrels_path))
    validate_dataset(documents, queries, qrels)
    return documents, queries, qrels


def build_qrels_dict(qrels: List[Qrel]) -> Dict[str, Dict[str, int]]:
    """Convert qrels list into qrels_dict[query_id][doc_id] = relevance."""
    qrels_dict: Dict[str, Dict[str, int]] = defaultdict(dict)
    for row in qrels:
        qrels_dict[row["query_id"]][row["doc_id"]] = int(row["relevance"])
    return dict(qrels_dict)


def print_statistics(documents: List[Document], queries: List[Query], qrels: List[Qrel]) -> None:
    """Print dataset statistics."""
    doc_categories = Counter(str(d.get("category", "") or "unknown") for d in documents)
    query_categories = Counter(str(q.get("category", "") or "unknown") for q in queries)
    query_types = Counter(str(q.get("query_type", "") or "unknown") for q in queries)
    relevance_counts = Counter(int(row["relevance"]) for row in qrels)
    relevant_pairs = sum(1 for row in qrels if int(row["relevance"]) > 0)
    qrels_by_query = Counter(row["query_id"] for row in qrels)

    print("\nKSE-Web dataset loaded successfully")
    print("=" * 42)
    print(f"Documents:                    {len(documents):,}")
    print(f"Queries:                      {len(queries):,}")
    print(f"Query-document labels:         {len(qrels):,}")
    print(f"Relevant pairs, rel > 0:       {relevant_pairs:,}")
    print(f"Avg. labeled docs per query:   {len(qrels) / max(len(queries), 1):.2f}")
    if qrels_by_query:
        print(f"Min labels/query:              {min(qrels_by_query.values())}")
        print(f"Max labels/query:              {max(qrels_by_query.values())}")

    print("\nDocument categories")
    for k, v in doc_categories.most_common():
        print(f"  {k}: {v}")

    print("\nQuery categories")
    for k, v in query_categories.most_common():
        print(f"  {k}: {v}")

    print("\nQuery types")
    for k, v in query_types.most_common():
        print(f"  {k}: {v}")

    print("\nRelevance labels")
    for rel in [2, 1, 0]:
        print(f"  {rel}: {relevance_counts.get(rel, 0)}")


def show_samples(documents: List[Document], queries: List[Query], qrels: List[Qrel], n: int = 3) -> None:
    """Print sample queries and their top labeled documents."""
    if n <= 0:
        return

    docs_by_id = {d["doc_id"]: d for d in documents}
    qrels_by_query = build_qrels_dict(qrels)

    print("\nSample queries")
    print("=" * 42)
    for query in queries[:n]:
        qid = query["query_id"]
        print(f"\n[{qid}] {query.get('query', '')}")
        print(f"  type={query.get('query_type', '')}, category={query.get('category', '')}")

        labeled_docs = qrels_by_query.get(qid, {})
        if not labeled_docs:
            print("  No qrels found.")
            continue

        for did, rel in sorted(labeled_docs.items(), key=lambda x: -x[1])[:5]:
            doc = docs_by_id.get(did, {})
            title = str(doc.get("title", ""))
            print(f"  rel={rel} doc_id={did} title={title[:100]}")


def export_to_hf_dataset(documents: List[Document], queries: List[Query], qrels: List[Qrel], output_dir: str | Path) -> None:
    """Export as a Hugging Face DatasetDict on disk. Requires: pip install datasets."""
    try:
        from datasets import Dataset, DatasetDict
    except ImportError as exc:
        raise ImportError("Install Hugging Face datasets first: pip install datasets") from exc

    dataset = DatasetDict({
        "documents": Dataset.from_list(documents),
        "queries": Dataset.from_list(queries),
        "qrels": Dataset.from_list(qrels),
    })
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset.save_to_disk(str(output_dir))
    print(f"\nSaved Hugging Face DatasetDict to: {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load and validate the KSE-Web dataset.")
    parser.add_argument("--data_dir", type=str, default="data", help="Directory containing documents.jsonl, queries.jsonl, and qrels.tsv.")
    parser.add_argument("--documents", type=str, default=None, help="Path to documents.jsonl.")
    parser.add_argument("--queries", type=str, default=None, help="Path to queries.jsonl.")
    parser.add_argument("--qrels", type=str, default=None, help="Path to qrels.tsv.")
    parser.add_argument("--sample", type=int, default=3, help="Number of sample queries to print. Use 0 to disable.")
    parser.add_argument("--export_hf_dir", type=str, default=None, help="Optional output directory for Hugging Face DatasetDict export.")
    args = parser.parse_args()

    try:
        documents, queries, qrels = load_kse_web(
            data_dir=args.data_dir,
            documents_path=args.documents,
            queries_path=args.queries,
            qrels_path=args.qrels,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print_statistics(documents, queries, qrels)
    show_samples(documents, queries, qrels, n=args.sample)

    if args.export_hf_dir:
        try:
            export_to_hf_dataset(documents, queries, qrels, args.export_hf_dir)
        except Exception as exc:
            print(f"Export error: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
