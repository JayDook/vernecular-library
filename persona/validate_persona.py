#!/usr/bin/env python3
"""Check every evidence reference in persona/*.md and persona_spec.json resolves to a repo record/source/letter."""
import json, glob, os, re, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
recs = {r["id"]: r for f in glob.glob(f"{R}/data/*.json") for r in json.load(open(f))["records"]}
srcs = {i["id"] for i in json.load(open(f"{R}/sources/manifest.json"))}
lets = {os.path.basename(f)[:-5] for f in glob.glob(f"{R}/correspondence/letters/*.json")}
errs, n = [], 0
for f in glob.glob(f"{R}/persona/*.md") + [f"{R}/persona/persona_spec.json"]:
    t = open(f).read()
    for m in re.finditer(r"\b((?:bio|time|pers|conv|op|world|sci|rel|dossier|pos|ex|contra)-\d{3})\b", t):
        n += 1; m.group(1) in recs or errs.append(f"{os.path.basename(f)}: unknown record {m.group(1)}")
    for m in re.finditer(r"src:([a-z0-9][a-z0-9-]*[a-z0-9])", t):
        n += 1; m.group(1) in srcs or errs.append(f"{os.path.basename(f)}: unknown source {m.group(1)}")
    for m in re.finditer(r"letter:([A-Za-z0-9_]+)", t):
        n += 1; m.group(1) in lets or errs.append(f"{os.path.basename(f)}: unknown letter {m.group(1)}")
    if re.search(r"(?:^|[\s'\"(])/(?:home|Users|tmp|work"r"space)/|[A-Z]:\\Users", t): errs.append(f"{os.path.basename(f)}: contains a box path")
spec = json.load(open(f"{R}/persona/persona_spec.json"))
for tr in spec["traits"]:
    for ref in tr["evidence_refs"]:
        if ref not in recs: errs.append(f"trait {tr['id']}: bad ref {ref}")
    low = [recs[r]["confidence"] for r in tr["evidence_refs"]]
    order = {"high": 2, "medium": 1, "low": 0}
    if order[tr["confidence"]] > max(order[c] for c in low): errs.append(f"trait {tr['id']}: confidence exceeds best evidence")
print(f"checked {n} references"); [print("ERROR", e) for e in errs]; sys.exit(1 if errs else 0)
