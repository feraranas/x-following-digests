# X Following digests

Immutable archive of categorized digests from [@FernandoArana_S](https://x.com/FernandoArana_S)'s X Following feed.

## Layout

- `digests/YYYY-MM-DD.md` — human-readable digest for that day (one section per window)
- `index.jsonl` — append-only machine index (one JSON object per post)
- `SCHEMA.md` — field definitions for `index.jsonl` (currently **v2**: `tweet_id`, `tags`, `entities`)

## Index fields (v2)

Each line includes: `schema_version`, `captured_at`, `window`, `category`, `author`, `handle`, `gist`, `tweet_url`, `tweet_id`, `type`, `tags`, `entities` (`people` / `products` / `papers` / `links`).

Git history is the audit trail — prefer append-only commits; do not rewrite past digests except for one-time schema migrations.
