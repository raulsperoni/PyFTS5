# PyFTS5

**PyFTS5** is a lightweight Python library that wraps an in‑memory SQLite database with FTS5 full‑text search capabilities. It provides a simple, Pythonic API to add documents (with optional IDs) and perform various full‑text searches using common operators. The library also leverages SQLite’s built‑in highlighting function to mark matched terms.

## Features

- **In‑Memory Database:** Uses an in‑memory SQLite database for fast, lightweight searches.
- **FTS5 Integration:** Leverages SQLite’s C‑implemented FTS5 extension for efficient full‑text indexing and search.
- **Document IDs:** Allows you to insert documents with specific IDs, so that search results carry a persistent identifier.
- **Helper Search Methods:** Supports common queries:
  - **Generic search:** Direct MATCH queries.
  - **Phrase search:** Exact phrase matching.
  - **Prefix search:** Match tokens beginning with a given prefix.
  - **Boolean operators:** AND, OR, NOT combinations.
  - **NEAR search:** Find terms within a specified distance.
- **Highlighting:** Optionally return search results with matched tokens highlighted (using SQLite’s `highlight()` function).
- **Context Manager:** Implements `__enter__` and `__exit__` so that the connection is automatically closed when finished.

## Installation

### Via Poetry

Clone the repository and run:

```bash
poetry install
```

If published on PyPI, install via pip:

```bash 
pip install PyFTS5
```

## Usage
Below is a quick example:

```python
from fts_search_db import FullTextSearchDB

# Prepare some documents as (doc_id, content) pairs.
docs = [
    (101, "The quick brown fox jumps over the lazy dog"),
    (102, "Never jump over the lazy dog quickly"),
    (103, "A quick movement of the enemy will jeopardize six gunboats"),
    (104, "Quick thinking leads to quick decisions"),
]

# Use the class as a context manager for automatic cleanup.
with FullTextSearchDB(docs) as fts_db:
    # Perform a generic search (without highlighting).
    results = fts_db.search("quick AND dog")
    for doc_id, content in results:
        print(f"Doc {doc_id}: {content}")

    # Perform a search with highlighting enabled.
    highlighted = fts_db.search("quick AND dog", highlight=True, hl_prefix="<<", hl_suffix=">>")
    for doc_id, hl_text, content in highlighted:
        print(f"Doc {doc_id} (highlighted): {hl_text}")
```

## Testing
Unit tests are written with pytest. To run the tests, simply run:

```bash
poetry run pytest
```

## License
This project is licensed under the MIT License.