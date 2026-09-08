# index.jsonl schema (v2)

One JSON object per line. Append-only after the initial enrichment migration.

## Required fields

| Field | Type | Notes |
|---|---|---|
| `schema_version` | number | Currently `2` |
| `captured_at` | string | ISO-8601 with offset (America/Mexico_City) |
| `window` | string | Digest window id (`08:00`, `12:00`, `16:00`, `20:00`, or `first-pull`) |
| `category` | string | Human section title for that digest |
| `author` | string | Display name |
| `handle` | string | `@username` |
| `gist` | string | One-line summary |
| `tweet_url` | string\|null | Full `https://x.com/.../status/<id>` URL |
| `tweet_id` | string\|null | Digits from `/status/<id>`; null if URL missing |
| `type` | string | `original` \| `repost` \| `quote` \| `reply` |
| `tags` | string[] | Controlled topic tags (lowercase kebab or single words) |
| `entities` | object | See below |

## `entities`

```json
{
  "people": ["@handle"],
  "products": ["name"],
  "papers": ["title or short id"],
  "links": ["https://..."]
}
```

Empty arrays are fine. Prefer extracting handles/products/papers mentioned in the post or gist.

## Optional fields

| Field | Type | Notes |
|---|---|---|
| `note` | string | e.g. `url_not_captured` |
| `signal` | string | Optional later: `technical` \| `actionable` \| `noise` |
| `enriched_at` | string | When enrichment was applied |

## Deduping

Prefer unique `tweet_id` when present. If the same status appears in a later window, skip or mark `duplicate_of` rather than inventing a second row.
