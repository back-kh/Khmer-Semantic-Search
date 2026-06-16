# Khmer Semantic Search (KSE)

**Khmer Semantic Search (KSE)** is a long-term research and development project for Khmer semantic search (KSE), Keyword Document Extraction (KDE) , digital information access, and Khmer Document Retrieval (KDR) in a low-resource language setting.

The goal of this project is to make Khmer information retrieval easier to study, test, and extend. It connects earlier Khmer semantic search work with newer web-based retrieval, hybrid search, and LLM-assisted query expansion. This public version is mainly released as a learning and research foundation for students, researchers, and developers interested in Khmer language technology.

---

## Table of Contents

- [Introduction](#introduction)
- [Research Background](#research-background)
- [Main Research Papers](#main-research-papers)
- [System Overview](#system-overview)
- [SEO and Search Analysis Reference](#seo-and-search-analysis-reference)
- [Datasets](#datasets)
- [KSWv2 Khmer Stop Word Dictionary Integration](#kswv2-khmer-stop-word-dictionary-integration)
- [KSE-Web and KSE-Web3K](#kse-web-and-kse-web3k)
- [Project Status](#project-status)
- [Getting Started](#getting-started)
- [Roadmap](#roadmap)
- [Citation](#citation)
- [Collaboration](#collaboration)
- [Author](#author)

---

## Introduction

Khmer Semantic Search (KSE) was created to address a long-standing gap in Khmer digital information access. Khmer content has grown rapidly across websites, reports, articles, social media, educational documents, tourism pages, and public information sources. However, searching Khmer content is still difficult because many search systems depend mainly on exact keyword matching, while Khmer language processing faces challenges such as word segmentation, compound words, spelling variation, limited annotated resources, and fewer public NLP tools compared with high-resource languages.

The first foundation of this project began as an early Khmer semantic search effort around 2014 and was later developed through academic and student-supported research. The foundational paper, **“Khmer Semantic Search Engine (KSE): Digital Information Access and Document Retrieval,”** was publicly released in 2024 on arXiv. Although the public paper appeared recently, the project itself reflects more than a decade of experimentation, dataset preparation, keyword extraction, stop-word filtering, ontology-based search, and ranking design.

KSE is designed as a practical research framework rather than only a single search application. It studies how Khmer queries can be processed, cleaned, expanded, matched, and ranked against document collections. The early version focuses on rule-based and semantic matching methods, including keyword dictionaries, ontology-based matching, and weighted ranking. The newer direction, **KSE-Web**, extends this foundation toward hybrid retrieval and LLM-assisted query expansion for low-resource Khmer semantic search.

This repository therefore serves three purposes:

1. **Research foundation** for Khmer semantic search and information retrieval.
2. **Educational resource** for Cambodian students and researchers learning NLP, search engines, and low-resource language processing.
3. **Development baseline** for future Khmer retrieval systems, including hybrid search, web search, query expansion, reranking, and retrieval-augmented generation.

---

## Research Background

Search engines normally retrieve documents by comparing user queries with indexed content. For Khmer, simple matching is often not enough because important meaning can be hidden by segmentation errors, missing spaces, compound forms, spelling differences, or different ways of writing the same concept. A user may search with one expression, while the relevant document uses another related expression.

The original KSE paper proposes a Khmer-specific semantic search framework to improve document access by extracting meaningful keywords from Khmer queries and documents, matching them with indexed content, and ranking the best offline documents or online URLs. The first framework includes:

- **Keyword dictionary-based semantic search**
- **Ontology-based semantic search**
- **Ranking-based semantic search**
- **Document and URL indexing**
- **Manual and automatic keyword extraction**
- **Ground-truth preparation for evaluation**

The project also highlights why Khmer search is important for education, tourism, public information, cultural content, and general digital access. Better Khmer search can help users find documents more accurately and can also support future Khmer NLP applications such as question answering, digital libraries, educational search, and RAG systems.

---

## Main Research Papers

### 1. Khmer Semantic Search Engine (KSE): Digital Information Access and Document Retrieval

- **Early project period:** around 2014-2016 (But released document in 2024)
- **Paper:** [arXiv:2406.09320](https://arxiv.org/abs/2406.09320)
- **Main focus:** Khmer semantic search, keyword extraction, ontology-based search, ranking, and document retrieval

This paper introduces the first Khmer Semantic Search Engine as a framework for improving Khmer document access. It focuses on extracting meaningful keywords from user queries and documents, matching queries with indexed content, and ranking relevant offline documents or online URLs. The paper also discusses Khmer language processing challenges, including limited resources, segmentation difficulty, complex writing forms, and the lack of high-accuracy search support for Khmer content.

The original KSE system includes both offline and online processing. Offline processing searches indexed documents stored in a database, while online processing is designed to retrieve and rank content from web pages. The system also uses Khmer stop-word filtering, keyword extraction, ontology-based expansion, and weighted ranking.

### 2. KSE-Web: An Analysis of Hybrid Retrieval and LLM-Assisted Query Expansion for Low-Resource Khmer Semantic Search

- **Status:** ongoing / foundation release
- **Main focus:** hybrid retrieval, LLM-assisted query expansion, and Khmer web search evaluation
- **Dataset:** [KSE-Web3K](https://huggingface.co/datasets/Backkh/KSE-Web3K)

KSE-Web is the next stage of the project. It studies how modern retrieval methods can improve Khmer search by combining traditional lexical search with semantic retrieval and query expansion. Instead of relying only on exact keyword matching, KSE-Web explores how an LLM can help rewrite or expand Khmer user queries so that retrieval systems can find more relevant documents.

This part is still being updated, so the public README explains only the high-level direction. More details about evaluation, model settings, prompts, ranking methods, and improved datasets will be added later.

---

## System Overview

KSE is organized around a practical retrieval pipeline:

```text
Khmer Query
   ↓
Preprocessing
   - normalization
   - tokenization / segmentation
   - stop-word removal
   - keyword extraction
   ↓
Semantic Processing
   - keyword dictionary matching
   - ontology-based expansion
   - optional LLM-assisted query expansion
   ↓
Retrieval
   - offline document retrieval
   - online URL / webpage retrieval
   - sparse retrieval
   - dense retrieval
   - hybrid retrieval
   ↓
Ranking
   - keyword score
   - semantic relevance
   - title/body weighting
   - relevance score / qrels evaluation
   ↓
Search Results
```

### Main Components

| Component | Purpose |
|---|---|
| Khmer preprocessing | Clean and prepare Khmer text for search |
| Stop-word filtering | Remove common function words that add little retrieval value |
| Keyword extraction | Identify important terms from titles, bodies, and queries |
| Ontology-based matching | Expand and connect concepts using structured domain knowledge |
| Sparse retrieval | Retrieve documents through lexical or keyword-based matching |
| Dense retrieval | Retrieve documents using embeddings and semantic similarity |
| Hybrid retrieval | Combine sparse and dense signals |
| LLM-assisted query expansion | Rewrite or enrich short Khmer queries with related terms |
| Ranking / reranking | Sort documents by relevance |
| Evaluation | Compare retrieved documents with ground-truth or silver relevance labels |

---
## SEO and Search Analysis Reference

An external SEO-focused analysis of the first KSE paper is available here:

**“Addressing the Gap: How the Khmer Semantic Search Engine (KSE) Works & What That Can Teach Us as SEOs”**  
Blog: [Ethan Lazuk / Hamsterdam Research](https://ethanlazuk.com/blog/hamsterdam-research-kse/)

This blog is useful because it explains KSE from a search-engine and SEO perspective. It discusses why Khmer semantic search matters, how the KSE framework relates to keyword extraction and semantic matching, and what search professionals can learn from low-resource language retrieval.

This reference is not part of the original KSE implementation, but it provides helpful external analysis for readers who want to understand KSE from a broader search and web-discovery perspective.

---
## Datasets

### Original KSE Dataset

The original KSE paper used a manually prepared dataset for Khmer document retrieval and keyword extraction. The early dataset was focused mainly on tourism, articles, web pages, blogs, news-like content, and social-media-style captions. The dataset was designed to test whether Khmer semantic matching can improve search results beyond simple keyword matching.

Main characteristics reported in the original KSE study:

- **1,150 Khmer documents/articles** collected and prepared for testing
- Manual keyword extraction with student support
- Title and body content used for keyword extraction
- Ground-truth preparation for evaluating search and ranking
- Top-ranked documents identified for query evaluation
- Evaluation using precision, recall, F1-score, and ranking-based comparison

This original dataset is useful for understanding the first KSE design, but it should be treated as a foundational research dataset, not a large-scale production benchmark.

### KSE-Web3K Dataset

**KSE-Web3K** is a newer silver-standard dataset for Khmer web retrieval and KSE-Web experiments.

- **Dataset page:** [Backkh/KSE-Web3K on Hugging Face](https://huggingface.co/datasets/Backkh/KSE-Web3K)
- **Type:** silver-standard retrieval dataset
- **Purpose:** training, testing, and evaluating Khmer semantic search and hybrid retrieval systems
- **License on Hugging Face:** CC BY-NC-ND 4.0

KSE-Web3K is intended for research and learning. It can support experiments such as:

- Khmer document retrieval
- query-document matching
- sparse retrieval baselines
- dense embedding retrieval
- hybrid retrieval
- LLM-assisted query expansion
- reranking experiments
- silver relevance evaluation

Expected dataset files include:

| File | Description |
|---|---|
| `documents.csv` | Khmer documents with document IDs, titles, text, categories, sources, URLs, and character counts |
| `queries.csv` | Khmer search queries for retrieval experiments |
| `qrels_silver_v2.csv` | Silver relevance labels connecting queries and documents |

> Note: The Hugging Face dataset viewer may not fully render all files together because the CSV files have different schemas. Users should load the files directly and treat `documents.csv`, `queries.csv`, and `qrels_silver_v2.csv` as separate retrieval components.

---

## KSWv2 Khmer Stop Word Dictionary Integration

This project connects with the Khmer stop-word dictionary project:

**KSWv2 Stop Word Dictionary for Khmer Document**  
Repository: [@back-kh/KSWv2-Stop-Word-Dictionary-for-Khmer-Document](https://github.com/back-kh/KSWv2-Stop-Word-Dictionary-for-Khmer-Document)

Stop-word filtering is important for Khmer semantic search because many frequent function words, particles, and filler words do not help identify the main meaning of a query or document. Removing these words can improve keyword extraction and make retrieval more focused.

KSWv2 provides:

- 300+ Khmer stop-word list for basic filtering
- 1000+ Khmer stop-word list for advanced filtering
- direct filtering examples
- filtering with Khmer word segmentation tools
- filtering examples using KhmerCUT and Khmer-NLTK

In KSE and KSE-Web, stop-word filtering can be used before keyword extraction, sparse retrieval, query expansion, and ranking.

---

## KSE-Web and KSE-Web3K

KSE-Web is a newer research direction that builds on the original KSE framework. The goal is to test whether modern retrieval methods can improve Khmer search while still remaining understandable and practical for low-resource settings.

### Main Idea

Traditional search may fail when the query and document use different words for related meanings. For example, a short query may not contain enough context, or the relevant document may use a related phrase instead of the exact query term. KSE-Web studies whether LLM-assisted query expansion can help by adding related terms, alternative expressions, or more complete context before retrieval.

### High-Level KSE-Web Pipeline

```text
User Query
   ↓
Khmer preprocessing + stop-word filtering
   ↓
LLM-assisted query expansion
   ↓
Sparse retrieval + dense retrieval
   ↓
Hybrid score fusion
   ↓
Reranking / relevance scoring
   ↓
Final Khmer search results
```

### Why KSE-Web3K Is Silver Data

KSE-Web3K is described as a silver-standard dataset because the relevance labels may be produced or assisted by automatic, semi-automatic, or weak-supervision methods. It is useful for building baselines and testing retrieval methods, but it should not be treated as a final gold-standard benchmark.

A stronger gold-standard version with more careful human verification is planned for future work. Some gold datasets and advanced functions are not included in this public foundation release.

---


## Project Status

This public repository is a **foundation release** for learning, research, and early experimentation.

Current focus:

- Khmer semantic search foundation
- keyword extraction and stop-word filtering
- original KSE paper documentation
- KSE-Web high-level direction
- KSE-Web3K dataset connection
- support for future hybrid retrieval experiments

Not all datasets and functions are public in this version. Some advanced functions and gold-standard datasets are reserved for future releases or research collaboration.

---

## Getting Started

### Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

### Installation

```bash
git clone https://github.com/back-kh/Khmer-Semantic-Search.git
cd Khmer-Semantic-Search
pip install -r requirements.txt
```

### Basic Use Cases

You can use this project as a starting point for:

- Khmer keyword extraction experiments
- Khmer stop-word filtering experiments
- document indexing and retrieval
- semantic search demonstrations
- query expansion experiments
- hybrid search baselines
- low-resource retrieval research
- educational NLP projects for Khmer language technology

---



## Citation

If this project is useful for your research, please cite the foundational KSE paper:

```bibtex
@misc{thuon2024kse,
  title={Khmer Semantic Search Engine (KSE): Digital Information Access and Document Retrieval},
  author={Thuon, Nimol},
  year={2024},
  eprint={2406.09320},
  archivePrefix={arXiv},
  primaryClass={cs.IR},
  url={https://arxiv.org/abs/2406.09320}
}
```

Related resources:

- KSE paper: <https://arxiv.org/abs/2406.09320>
- KSE-Web3K dataset: <https://huggingface.co/datasets/Backkh/KSE-Web3K>
- KSWv2 Khmer Stop Word Dictionary: <https://github.com/back-kh/KSWv2-Stop-Word-Dictionary-for-Khmer-Document>
- SEO analysis blog: <https://ethanlazuk.com/blog/hamsterdam-research-kse/>

---

## Collaboration

This project has been a long journey. After 12 years, I am happy to share this new version as a foundation for researchers, especially Cambodian students and researchers working on Khmer language technology.

Most of this work has been driven by personal interest and has been mostly self-funded. Progress has sometimes been slower than I hoped, but I remain passionate about contributing to the Khmer research community.

A stronger and more advanced version is planned in the future. The current public releases are mainly foundations for learning and research. Some gold-standard datasets and advanced functions are not fully public yet. If industry teams, universities, or researchers would like to collaborate on Khmer search, Khmer NLP, low-resource retrieval, or gold dataset development, please contact me.

---

## Author

**Nimol Thuon**

For collaboration, research partnerships, discussion, or advanced implementation, please contact me directly.

---

*Advancing Khmer Language Technology for the Future.*
