#!/usr/bin/env python3
"""Search the corpus.  Examples:
  python3 scripts/search.py "Hetzel"                     # FTS5 query
  python3 scripts/search.py '"Amiens" NEAR(religion, 20)' --lang en
  python3 scripts/search.py ballon --category works -n 5
Accent-insensitive (unicode61 remove_diacritics). Supports FTS5 syntax: AND OR NOT, "phrases", prefix*, NEAR()."""
import argparse, os, sqlite3
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument("query"); ap.add_argument("--lang"); ap.add_argument("--category"); ap.add_argument("-n", type=int, default=10)
a = ap.parse_args()
db = os.path.join(ROOT, "index/verne.db")
if not os.path.exists(db): raise SystemExit("index missing: run python3 scripts/build_index.py")
c = sqlite3.connect(db)
sql = "SELECT p.doc_id, p.chunk, p.offset, coalesce(d.title,p.doc_id), snippet(passages,5,'[',']',' … ',24) FROM passages p LEFT JOIN docs d ON d.id=p.doc_id WHERE passages MATCH ?"
args = [a.query]
if a.lang: sql += " AND p.language=?"; args.append(a.lang)
if a.category: sql += " AND p.category=?"; args.append(a.category)
sql += " ORDER BY rank LIMIT ?"; args.append(a.n)
for doc, ch, off, title, snip in c.execute(sql, args):
    print(f"{doc}  [chunk {ch}, char {off}]  {title[:60]}\n    {snip.replace(chr(10),' ')}\n")
