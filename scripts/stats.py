#!/usr/bin/env python3
"""Corpus counts used by COVERAGE_REPORT.md -> sources/stats.json"""
import json, os, collections, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = json.load(open(os.path.join(ROOT, "sources/manifest.json")))
st = collections.Counter(i["status"].split(" -")[0] for i in m)
col = [i for i in m if i["status"] == "collected"]
out = {"items_total": len(m), "by_status": st,
       "collected_by_category_language": collections.Counter(f'{i["category"]}/{i["language"]}' for i in col),
       "collected_by_type": collections.Counter(i["type"] for i in col),
       "collected_chars_total": sum(i["chars"] for i in col),
       "merged_duplicates": len(json.load(open(os.path.join(ROOT, "sources/dedup_log.json")))),
       "claims": {os.path.basename(f)[:-5]: collections.Counter(r["evidence_level"] for r in json.load(open(f))["records"]) for f in sorted(glob.glob(os.path.join(ROOT, "data/*.json")))}}
json.dump(out, open(os.path.join(ROOT, "sources/stats.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
