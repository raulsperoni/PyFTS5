import sqlite3

import pytest
from pyfts5.core import (
    FullTextSearchDB,
)


@pytest.fixture
def sample_db():
    # Sample documents: each is a (doc_id, content) tuple.
    docs = [
        (101, "The quick brown fox jumps over the lazy dog"),
        (102, "Never jump over the lazy dog quickly"),
        (103, "A quick movement of the enemy will jeopardize six gunboats"),
        (104, "Quick thinking leads to quick decisions"),
    ]
    db = FullTextSearchDB(docs)
    yield db
    db.close()


def test_generic_search(sample_db):
    results = sample_db.search("quick AND dog")
    # Check that at least one document matches.
    assert len(results) > 0
    # Ensure that doc_id 101 is among the results.
    doc_ids = [row[0] for row in results]
    assert 101 in doc_ids


def test_search_phrase(sample_db):
    results = sample_db.search_phrase("quick brown", highlight=False)
    # Expect document 101 to match the exact phrase.
    doc_ids = [row[0] for row in results]
    assert 101 in doc_ids


def test_search_prefix(sample_db):
    results = sample_db.search_prefix("qui", highlight=False)
    # At least one document should match the prefix search.
    assert len(results) > 0


def test_search_and(sample_db):
    results = sample_db.search_and(["quick", "decisions"], highlight=False)
    # Expect document 104 to contain both terms.
    doc_ids = [row[0] for row in results]
    assert 104 in doc_ids


def test_search_or(sample_db):
    results = sample_db.search_or(["enemy", "lazy"], highlight=False)
    # Expect at least one document from doc_ids 101, 102, or 103.
    doc_ids = [row[0] for row in results]
    assert any(doc in doc_ids for doc in [101, 102, 103])


def test_search_not(sample_db):
    # Search for documents containing "quick" but NOT "brown".
    results = sample_db.search_not("quick", "brown", highlight=False)
    # Document 104 should match.
    doc_ids = [row[0] for row in results]
    assert 104 in doc_ids


def test_search_near(sample_db):
    results = sample_db.search_near(
        ["quick", "enemy"], max_distance=10, highlight=False
    )
    # At least one document should match the NEAR condition.
    assert len(results) > 0


def test_highlight_option(sample_db):
    # Test that search returns highlighted text when highlight=True.
    results = sample_db.search("quick", highlight=True, hl_prefix="<<", hl_suffix=">>")
    for row in results:
        rowid, highlighted, content = row
        assert "<<" in highlighted
        assert ">>" in highlighted


def test_context_manager():
    # Test that the context manager (__enter__/__exit__) closes the connection.
    with FullTextSearchDB([(201, "Sample document for context manager")]) as db:
        results = db.search("Sample")
        assert len(results) > 0
    # After exiting the with-block, accessing the connection should fail.
    with pytest.raises(sqlite3.ProgrammingError):
        db.conn.execute("SELECT 1")
