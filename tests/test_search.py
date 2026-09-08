#!/usr/bin/env python3
"""Unit / integration tests for tools/search.py.

Harness shape:
- Fixture JSONL under tests/fixtures/ (stable, not the live digest).
- Temp SQLite DB per test class (real sqlite3 FTS5).
- Import search module functions directly; also smoke the CLI via main().

Run: python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "sample_index.jsonl"

sys.path.insert(0, str(TOOLS))
import search  # noqa: E402


class SearchHarnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not FIXTURE.exists():
            raise FileNotFoundError(f"missing fixture: {FIXTURE}")
        cls._tmpdir = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls._tmpdir.name) / "test.sqlite"
        cls.conn = search.connect(cls.db_path)
        cls.count = search.rebuild(cls.conn, FIXTURE)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.conn.close()
        cls._tmpdir.cleanup()

    def test_rebuild_loads_all_fixture_rows(self) -> None:
        self.assertEqual(self.count, 5)
        n = self.conn.execute("SELECT COUNT(*) AS c FROM posts").fetchone()["c"]
        self.assertEqual(n, 5)

    def test_fts_agent_finds_expected_handles(self) -> None:
        rows = search.search(self.conn, "agent", None, None, limit=20)
        handles = {r["handle"] for r in rows}
        self.assertIn("@dair_ai", handles)
        self.assertIn("@rauchg", handles)
        self.assertIn("@addyosmani", handles)
        self.assertNotIn("@threejs", handles)

    def test_fts_memory_single_hit(self) -> None:
        rows = search.search(self.conn, "memory", None, None, limit=20)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["handle"], "@dair_ai")
        self.assertEqual(rows[0]["tweet_id"], "2096985097450999839")

    def test_handle_filter_rauchg(self) -> None:
        rows = search.search(self.conn, None, "rauchg", None, limit=20)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["handle"] == "@rauchg" for r in rows))

    def test_tag_filter_agents(self) -> None:
        rows = search.search(self.conn, None, None, "agents", limit=20)
        handles = {r["handle"] for r in rows}
        self.assertEqual(handles, {"@dair_ai"})

    def test_combined_query_and_handle(self) -> None:
        rows = search.search(self.conn, "agent", "rauchg", None, limit=20)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["handle"] == "@rauchg" for r in rows))

    def test_no_matches(self) -> None:
        rows = search.search(self.conn, "zzzznotarealtoken", None, None, limit=20)
        self.assertEqual(rows, [])

    def test_fts_hyphenated_query_does_not_error(self) -> None:
        # Regression: unquoted hyphens used to raise OperationalError in FTS5
        rows = search.search(self.conn, "zzzz-not-a-real-token", None, None, limit=20)
        self.assertEqual(rows, [])

    def test_rebuild_is_idempotent(self) -> None:
        n1 = search.rebuild(self.conn, FIXTURE)
        n2 = search.rebuild(self.conn, FIXTURE)
        self.assertEqual(n1, n2)
        n = self.conn.execute("SELECT COUNT(*) AS c FROM posts").fetchone()["c"]
        self.assertEqual(n, 5)


class SearchCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "cli.sqlite"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_cli_memory_smoke(self) -> None:
        buf = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            code = search.main(
                [
                    "memory",
                    "--index",
                    str(FIXTURE),
                    "--db",
                    str(self.db_path),
                    "--rebuild",
                ]
            )
        self.assertEqual(code, 0)
        out = buf.getvalue()
        self.assertIn("1 match", out)
        self.assertIn("@dair_ai", out)
        self.assertIn("2096985097450999839", out)

    def test_cli_requires_query_or_filter(self) -> None:
        with self.assertRaises(SystemExit):
            search.main(["--db", str(self.db_path), "--index", str(FIXTURE)])


if __name__ == "__main__":
    unittest.main()
