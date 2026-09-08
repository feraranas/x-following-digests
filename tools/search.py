#!/usr/bin/env python3
"""Search X Following digests via SQLite FTS5.

Source of truth: index.jsonl (schema v2). The SQLite file is a rebuildable cache.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "index.jsonl"
DEFAULT_DB = ROOT / ".cache" / "digests.sqlite"


def join_list(value) -> str:
    if not value:
        return ""
    if isinstance(value, list):
        return " ".join(str(x) for x in value if x)
    return str(value)


def fts_match_query(query: str) -> str:
    """Quote user terms so FTS5 does not treat punctuation as operators.

    Hyphens otherwise become unary NOT / column syntax and raise OperationalError.
    """
    tokens = [t for t in query.replace('"', " ").split() if t]
    if not tokens:
        return '""'
    return " ".join(f'"{t}"' for t in tokens)


def flatten_entities(entities: dict | None) -> tuple[str, str, str, str]:
    entities = entities or {}
    return (
        join_list(entities.get("people")),
        join_list(entities.get("products")),
        join_list(entities.get("papers")),
        join_list(entities.get("links")),
    )


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP TABLE IF EXISTS posts_fts;
        DROP TABLE IF EXISTS posts;

        CREATE TABLE posts (
            id INTEGER PRIMARY KEY,
            schema_version INTEGER,
            captured_at TEXT,
            window TEXT,
            category TEXT,
            author TEXT,
            handle TEXT,
            gist TEXT,
            tweet_url TEXT,
            tweet_id TEXT,
            type TEXT,
            tags TEXT,
            people TEXT,
            products TEXT,
            papers TEXT,
            links TEXT,
            note TEXT,
            raw_json TEXT NOT NULL
        );

        CREATE VIRTUAL TABLE posts_fts USING fts5(
            gist,
            category,
            handle,
            author,
            tags,
            people,
            products,
            papers,
            content='posts',
            content_rowid='id'
        );
        """
    )


def rebuild(conn: sqlite3.Connection, index_path: Path) -> int:
    if not index_path.exists():
        raise FileNotFoundError(f"index not found: {index_path}")

    init_schema(conn)
    count = 0
    with index_path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_no}: {exc}") from exc

            people, products, papers, links = flatten_entities(row.get("entities"))
            tags = join_list(row.get("tags"))
            cur = conn.execute(
                """
                INSERT INTO posts (
                    schema_version, captured_at, window, category, author, handle,
                    gist, tweet_url, tweet_id, type, tags, people, products, papers,
                    links, note, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("schema_version"),
                    row.get("captured_at"),
                    row.get("window"),
                    row.get("category"),
                    row.get("author"),
                    row.get("handle"),
                    row.get("gist"),
                    row.get("tweet_url"),
                    row.get("tweet_id"),
                    row.get("type"),
                    tags,
                    people,
                    products,
                    papers,
                    links,
                    row.get("note"),
                    line,
                ),
            )
            rowid = cur.lastrowid
            conn.execute(
                """
                INSERT INTO posts_fts (
                    rowid, gist, category, handle, author, tags, people, products, papers
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rowid,
                    row.get("gist") or "",
                    row.get("category") or "",
                    row.get("handle") or "",
                    row.get("author") or "",
                    tags,
                    people,
                    products,
                    papers,
                ),
            )
            count += 1
    conn.commit()
    return count


def ensure_loaded(conn: sqlite3.Connection, index_path: Path, force: bool) -> None:
    exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='posts'"
    ).fetchone()
    if force or not exists:
        n = rebuild(conn, index_path)
        print(f"rebuilt cache from {index_path} ({n} posts)", file=sys.stderr)
        return
    n = conn.execute("SELECT COUNT(*) AS c FROM posts").fetchone()["c"]
    if n == 0:
        n = rebuild(conn, index_path)
        print(f"rebuilt empty cache from {index_path} ({n} posts)", file=sys.stderr)


def search(
    conn: sqlite3.Connection,
    query: str | None,
    handle: str | None,
    tag: str | None,
    limit: int,
) -> list[sqlite3.Row]:
    clauses: list[str] = []
    params: list[object] = []

    if query:
        clauses.append("posts.id IN (SELECT rowid FROM posts_fts WHERE posts_fts MATCH ?)")
        params.append(fts_match_query(query))

    if handle:
        h = handle if handle.startswith("@") else f"@{handle}"
        clauses.append("LOWER(posts.handle) = LOWER(?)")
        params.append(h)

    if tag:
        # tags stored space-separated; match whole token case-insensitively
        clauses.append("(' ' || LOWER(posts.tags) || ' ') LIKE ?")
        params.append(f"% {tag.lower()} %")
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"""
        SELECT captured_at, window, category, author, handle, gist,
               tweet_url, tweet_id, type, tags, people, products, papers, note
        FROM posts
        {where}
        ORDER BY captured_at DESC, id DESC
        LIMIT ?
    """
    params.append(limit)
    return list(conn.execute(sql, params))


def format_row(row: sqlite3.Row) -> str:
    url = row["tweet_url"] or "(no url)"
    tags = row["tags"] or ""
    lines = [
        f"- {row['handle']} · {row['category']} · {row['captured_at']}",
        f"  {row['gist']}",
        f"  {url}",
    ]
    if tags:
        lines.append(f"  tags: {tags}")
    if row["tweet_id"]:
        lines.append(f"  tweet_id: {row['tweet_id']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Search X Following digests (SQLite FTS5 over index.jsonl)"
    )
    parser.add_argument("query", nargs="?", help="FTS5 query, e.g. agent OR memory")
    parser.add_argument("--handle", help="Filter by @handle")
    parser.add_argument("--tag", help="Filter by a single tag token")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default 20)")
    parser.add_argument(
        "--index",
        type=Path,
        default=DEFAULT_INDEX,
        help=f"Path to index.jsonl (default: {DEFAULT_INDEX})",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help=f"SQLite cache path (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force rebuild the SQLite cache from index.jsonl",
    )
    args = parser.parse_args(argv)

    if not args.query and not args.handle and not args.tag:
        parser.error("provide a query and/or --handle / --tag")

    conn = connect(args.db)
    try:
        ensure_loaded(conn, args.index, force=args.rebuild)
        rows = search(conn, args.query, args.handle, args.tag, args.limit)
    finally:
        conn.close()

    if not rows:
        print("no matches")
        return 0

    print(f"{len(rows)} match(es)\n")
    print("\n\n".join(format_row(r) for r in rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
