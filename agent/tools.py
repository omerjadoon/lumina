import os

import bm25s

MAX_CHARS = 8000
CHUNK_SIZE = 500  # chars per passage

_retriever: bm25s.BM25 | None = None
_passages: list[tuple[str, str]] | None = None  # (filename, text) parallel to corpus


def _chunk(text: str) -> list[str]:
    return [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]


def build_index(directory: str) -> None:
    """Build BM25 index over .txt files in directory (no API calls required)."""
    global _retriever, _passages
    if _retriever is not None:
        return

    raw_passages: list[tuple[str, str]] = []
    for filename in sorted(f for f in os.listdir(directory) if f.endswith(".txt")):
        path = os.path.join(directory, filename)
        try:
            text = open(path, encoding="utf-8").read()
        except OSError:
            continue
        for chunk in _chunk(text):
            raw_passages.append((filename, chunk))

    if not raw_passages:
        _retriever = bm25s.BM25()
        _passages = []
        return

    corpus = [p[1] for p in raw_passages]
    tokenized = bm25s.tokenize(corpus)
    retriever = bm25s.BM25()
    retriever.index(tokenized)
    _retriever = retriever
    _passages = raw_passages


def search_corpus(directory: str, query: str, top_k: int = 3) -> str:
    """BM25 search across the indexed corpus. Returns top-k passages with source filenames."""
    if _retriever is None:
        build_index(directory)
    if not _passages:
        return "(corpus index is empty)"

    q_tokens = bm25s.tokenize([query])
    results, _ = _retriever.retrieve(q_tokens, k=min(top_k, len(_passages)))
    parts = []
    for idx in results[0]:
        filename, text = _passages[int(idx)]
        parts.append(f"=== {filename} ===\n{text}")
    return "\n\n".join(parts)


def list_files(directory: str) -> list[str]:
    """Return sorted filenames in directory. Returns [] if directory is absent or unreadable."""
    try:
        return sorted(
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        )
    except OSError:
        return []


def read_file(directory: str, filename: str) -> str:
    """Return up to MAX_CHARS characters of filename. Returns '' if file is absent or unreadable."""
    path = os.path.join(directory, filename)
    try:
        with open(path, encoding="utf-8") as fh:
            content = fh.read(MAX_CHARS)
        return content
    except OSError:
        return ""


def search_in_file(directory: str, filename: str, query: str) -> str:
    """Return newline-joined lines containing query (case-insensitive). Returns '' on no match or missing file."""
    path = os.path.join(directory, filename)
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError:
        return ""

    needle = query.lower()
    matches = [line.rstrip() for line in lines if needle in line.lower()]
    return "\n".join(matches)
