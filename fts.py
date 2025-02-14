import sqlite3


class FullTextSearchDB:
    """
    A lightweight wrapper for an in‑memory SQLite database using FTS5.

    Documents are stored in a virtual table named "documents" with a single
    text column. Each document can be inserted with a specific id (mapping to the
    hidden rowid) so that search results include a persistent identifier.
    The search methods include an optional "highlight" mode that uses SQLite’s
    built-in highlight() function to mark matched terms.
    """

    def __init__(self, documents=None):
        # Create an in-memory SQLite database.
        self.conn = sqlite3.connect(":memory:")
        self.conn.enable_load_extension(True)
        try:
            # Create the FTS5 virtual table.
            self.conn.execute("CREATE VIRTUAL TABLE documents USING fts5(content)")
        except sqlite3.OperationalError as e:
            raise RuntimeError(
                "FTS5 extension not available in this SQLite build."
            ) from e
        # Optionally, add initial documents.
        if documents:
            # documents is expected to be an iterable of (doc_id, content) pairs.
            self.add_documents(documents)

    # Context manager methods:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def add_document(self, content, doc_id=None):
        """
        Add a single document (a string) to the index.

        If 'doc_id' is provided, it will be used as the rowid for the document.
        """
        if doc_id is not None:
            self.conn.execute(
                "INSERT INTO documents(rowid, content) VALUES (?, ?)", (doc_id, content)
            )
        else:
            self.conn.execute("INSERT INTO documents(content) VALUES (?)", (content,))
        self.conn.commit()

    def add_documents(self, docs):
        """
        Bulk add multiple documents.

        'docs' should be an iterable of (doc_id, content) tuples. If doc_id is None,
        a new rowid will be assigned.
        """
        params = []
        for doc_id, content in docs:
            if doc_id is not None:
                params.append((doc_id, content))
            else:
                params.append((content,))
        # Assume all docs are of the same type.
        if params and len(params[0]) == 2:
            self.conn.executemany(
                "INSERT INTO documents(rowid, content) VALUES (?, ?)", params
            )
        else:
            self.conn.executemany("INSERT INTO documents(content) VALUES (?)", params)
        self.conn.commit()

    def search(self, query, highlight=False, hl_prefix="<b>", hl_suffix="</b>"):
        """
        Perform a full-text search using the given query string.

        If highlight is True, uses SQLite's highlight() function on the
        first column (the only column) to return highlighted text.

        When highlight is False, returns a list of (rowid, content) tuples.
        When highlight is True, returns a list of (rowid, highlighted, content)
        tuples.
        """
        if highlight:
            sql = """
            SELECT rowid,
                   highlight(documents, 0, ?, ?) AS highlighted,
                   content
            FROM documents
            WHERE documents MATCH ?
            """
            cursor = self.conn.execute(sql, (hl_prefix, hl_suffix, query))
        else:
            sql = "SELECT rowid, content FROM documents WHERE documents MATCH ?"
            cursor = self.conn.execute(sql, (query,))
        return cursor.fetchall()

    # Helper search methods pass through the highlight options:
    def search_phrase(self, phrase, **kwargs):
        """Exact phrase search by quoting the phrase."""
        query = f'"{phrase}"'
        return self.search(query, **kwargs)

    def search_prefix(self, prefix, **kwargs):
        """Prefix search: appends an asterisk."""
        query = f"{prefix}*"
        return self.search(query, **kwargs)

    def search_and(self, terms, **kwargs):
        """Boolean AND search for all terms."""
        if isinstance(terms, str):
            terms = [terms]
        query = " AND ".join(terms)
        return self.search(query, **kwargs)

    def search_or(self, terms, **kwargs):
        """Boolean OR search for any of the terms."""
        if isinstance(terms, str):
            terms = [terms]
        query = " OR ".join(terms)
        return self.search(query, **kwargs)

    def search_not(self, include_term, exclude_term, **kwargs):
        """Search for documents containing include_term but not exclude_term."""
        query = f"{include_term} NOT {exclude_term}"
        return self.search(query, **kwargs)

    def search_near(self, terms, max_distance=10, **kwargs):
        """
        NEAR search for documents with terms within max_distance tokens.
        """
        if isinstance(terms, str):
            terms = [terms]
        query = f"NEAR({' '.join(terms)}, {max_distance})"
        return self.search(query, **kwargs)

    def close(self):
        """Close the underlying SQLite connection."""
        self.conn.close()
