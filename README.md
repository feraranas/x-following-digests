# X Following digests

Immutable archive of categorized digests from [@FernandoArana_S](https://x.com/FernandoArana_S)'s X Following feed.

## Layout

- `digests/YYYY-MM-DD.md` — human-readable digest for that day (one section per window)
- `index.jsonl` — append-only machine index (one JSON object per post)
- `SCHEMA.md` — field definitions for `index.jsonl` (currently **v2**: `tweet_id`, `tags`, `entities`)
- `tools/search.py` — local SQLite FTS5 search over `index.jsonl`

## Index fields (v2)

Each line includes: `schema_version`, `captured_at`, `window`, `category`, `author`, `handle`, `gist`, `tweet_url`, `tweet_id`, `type`, `tags`, `entities` (`people` / `products` / `papers` / `links`).

Git history is the audit trail — prefer append-only commits; do not rewrite past digests except for one-time schema migrations.

## Search (SQLite FTS5)

`index.jsonl` stays the source of truth. `tools/search.py` rebuilds a local cache at `.cache/digests.sqlite` (gitignored).

```bash
# full-text search
python3 tools/search.py agent

# filter by handle / tag
python3 tools/search.py --handle rauchg
python3 tools/search.py --tag agents

# combine + force rebuild
python3 tools/search.py memory --tag agents --rebuild
```

Stdlib only (`sqlite3` + `argparse`).
