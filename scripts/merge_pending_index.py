#!/usr/bin/env python3
"""Append pending/*.jsonl into index.jsonl (dedupe by tweet_id), then delete pending files."""
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    index_path = Path("index.jsonl")
    pending_dir = Path("pending")
    known: set[str] = set()
    rows: list[dict] = []

    if index_path.exists():
        for line in index_path.read_text().splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            rows.append(obj)
            tid = str(obj.get("tweet_id") or "")
            if tid:
                known.add(tid)

    added = 0
    removed: list[str] = []
    if pending_dir.exists():
        for pending in sorted(pending_dir.glob("*.jsonl")):
            for line in pending.read_text().splitlines():
                if not line.strip():
                    continue
                obj = json.loads(line)
                tid = str(obj.get("tweet_id") or "")
                if tid and tid in known:
                    continue
                rows.append(obj)
                if tid:
                    known.add(tid)
                added += 1
            pending.unlink()
            removed.append(str(pending))

    index_path.write_text(
        "".join(
            json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows
        )
    )
    print(f"added={added} total={len(rows)} removed={removed}")


if __name__ == "__main__":
    main()
