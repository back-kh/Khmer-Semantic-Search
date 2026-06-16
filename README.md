# Khmer Semantic Search (KSE)

Khmer Semantic Search (KSE) is a long-term project for Khmer semantic search, digital information access, and document retrieval in a low-resource language setting.

## Introduction

Khmer Semantic Search represents a comprehensive initiative to advance information retrieval and natural language processing for the Khmer language. This project bridges the gap in semantic search technology for low-resource languages, enabling better digital information access and document retrieval capabilities.

The foundation of this work traces back to early research in 2014, with the original paper *Khmer Semantic Search Engine (KSE): Digital Information Access and Document Retrieval* (https://arxiv.org/abs/2406.09320). After more than a decade of development, recent publications in 2024 bring renewed focus to modern approaches in Khmer semantic search.

## Research & Publications

### Papers

- **2014:** *Khmer Semantic Search Engine (KSE): Digital Information Access and Document Retrieval*
  - Original foundational research in semantic search for Khmer language
  
- **2024:** *KSE-Web: An Analysis of Hybrid Retrieval and LLM-Assisted Query Expansion for Low-Resource Khmer Semantic Search*
  - Recent advancement exploring hybrid retrieval methods and LLM-assisted query expansion techniques
  - Reference: https://arxiv.org/abs/2406.09320

### Referenced Analysis

- **SEO Expert Analysis:** [Hamsterdam Research - KSE](https://ethanlazuk.com/blog/hamsterdam-research-kse/)
  - Independent analysis and insights on Khmer Semantic Search approaches

## Datasets

### KSE-Web3K Dataset
This project utilizes the **KSE-Web3K** dataset, a silver-standard corpus available on Hugging Face:

- **Dataset URL:** https://huggingface.co/datasets/Backkh/KSE-Web3K
- **Type:** Silver-standard dataset for Khmer semantic search
- **Purpose:** Foundation for training and evaluation of semantic search models

## Stopword Dictionary Integration

This project integrates with the **KSWv2 Stop Word Dictionary for Khmer Document**, providing essential linguistic preprocessing capabilities for Khmer text processing.

- **Related Project:** [@back-kh/KSWv2-Stop-Word-Dictionary-for-Khmer-Document](https://github.com/back-kh/KSWv2-Stop-Word-Dictionary-for-Khmer-Document)
- **Purpose:** Remove common Khmer stopwords to improve semantic search quality

## About

This project has been a long journey. After 12 years of development, I am happy to share this new version as a foundation for researchers, especially Cambodian students and researchers working on Khmer language technology.

Most of this work has been driven by personal interest and largely self-funded. Progress has sometimes been slower than I hoped, but I remain passionate about contributing to the Khmer research community.

### Future Developments

This version serves as a foundation for learning purposes. Enhanced versions with gold-standard datasets and advanced functionalities are under development. These gold-datasets and enhanced functions are being reserved for special releases designed to provide more robust and comprehensive tools for the community.

**For researchers and industry partners** interested in collaboration on advanced versions or specialized implementations, please contact the author for partnership opportunities.

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

## License

This project is shared for research and educational purposes within the Khmer research community.

## Author

**Nimol Thuon**

For inquiries regarding collaboration, research partnerships, or advanced implementations, please reach out directly.

---

*Advancing Khmer Language Technology for the Future*
