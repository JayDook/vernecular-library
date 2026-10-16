#!/usr/bin/env python3
"""Build SQLite FTS5 full-text index at index/verne.db from manifest + data/*.json.
Texts are chunked into ~1500-char passages so hits have a precise location (chunk number, char offset)."""
import json, os, sqlite3, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def main():
    os.makedirs(os.path.join(ROOT, "index"), exist_ok=True)
    db = os.path.join(ROOT, "index/verne.db")
    if os.path.exists(db): os.remove(db)
    c = sqlite3.connect(db)
    c.execute("CREATE TABLE docs(id TEXT PRIMARY KEY, title TEXT, author TEXT, language TEXT, category TEXT, date TEXT, file_path TEXT)")
    c.execute("CREATE VIRTUAL TABLE passages USING fts5(doc_id UNINDEXED, chunk UNINDEXED, offset UNINDEXED, language UNINDEXED, category UNINDEXED, text, tokenize='unicode61 remove_diacritics 2')")
    n = 0
    for it in json.load(open(os.path.join(ROOT, "sources/manifest.json"))):
        if it["status"] != "collected": continue
        c.execute("INSERT INTO docs VALUES(?,?,?,?,?,?,?)", (it["id"], it["title"], it["author"], it["language"], it["category"], it["date"], it["file_path"]))
        t = open(os.path.join(ROOT, it["file_path"]), encoding="utf-8").read()
        paras, buf, off, start, k = t.split("\n\n"), "", 0, 0, 0
        for p in paras:
            if len(buf) + len(p) > 1500 and buf:
                c.execute("INSERT INTO passages VALUES(?,?,?,?,?,?)", (it["id"], k, start, it["language"], it["category"], buf)); k += 1; n += 1
                buf, start = "", off
            buf += p + "\n\n"; off += len(p) + 2
        if buf.strip(): c.execute("INSERT INTO passages VALUES(?,?,?,?,?,?)", (it["id"], k, start, it["language"], it["category"], buf)); n += 1
    for f in sorted(glob.glob(os.path.join(ROOT, "data/*.json"))):
        name = os.path.basename(f)
        for i, rec in enumerate(json.load(open(f)).get("records", [])):
            c.execute("INSERT INTO passages VALUES(?,?,?,?,?,?)", ("data/" + name, i, 0, "en", "structured", json.dumps(rec, ensure_ascii=False))); n += 1
    # correspondence: archival descriptions (librarian summaries) and UNVERIFIED machine HTR, labelled by category
    for f in sorted(glob.glob(os.path.join(ROOT, "correspondence/letters/*.json"))):
        L = json.load(open(f)); lid = "letter:" + L["id"]
        ad = (L.get("archival_description") or {}).get("text")
        if ad: c.execute("INSERT INTO passages VALUES(?,?,?,?,?,?)", (lid, 0, 0, "fr", "archival_description", f"{L['cote']} | {L['title']} | {L.get('date')}\n{ad}")); n += 1
        if L.get("transcription_excerpt"): c.execute("INSERT INTO passages VALUES(?,?,?,?,?,?)", (lid, 1, 0, "fr", "archival_transcription_unverified", L["transcription_excerpt"])); n += 1
        if L["transcription_status"] == "machine_htr":
            h = json.load(open(os.path.join(ROOT, L["transcription_file"])))
            c.execute("INSERT INTO passages VALUES(?,?,?,?,?,?)", (lid, 2, 0, "fr", "machine_htr_unverified", h["text"])); n += 1
    c.commit(); print(n, "passages indexed ->", db)
if __name__ == "__main__": main()
