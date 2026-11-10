"""Measure extraction quality on documents the system was NOT tuned on.

Run from the ai-service folder with an LLM configured (see .env.example):

    python -m eval.run_eval              # LLM extractor only
    python -m eval.run_eval --classic    # classic ML pipeline for comparison

Metrics per document and overall:
  - date recall      : gold dates that were found
  - date precision   : extracted dates that are in the gold set
  - kind accuracy    : found dates whose deadline/event/info meaning is right
  - false tasks      : tasks suggested for dates that need no action

Add your own real notices to documents.json (with hand-labelled gold dates) to
grow the test set. Numbers from a few documents are a smoke test, not a benchmark.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from app.ml import llm_extractor  # noqa: E402

ACTIONABLE_GOLD = {"deadline", "event"}


def run(use_classic: bool, today: date) -> int:
    docs = json.loads((HERE / "documents.json").read_text(encoding="utf-8"))
    cfg = llm_extractor.load_config()
    if not use_classic and not cfg.enabled:
        print("LLM not configured. Set LLM_PROVIDER, LLM_API_KEY, LLM_MODEL (see .env.example).")
        return 2
    if use_classic:
        from app.ml import deadline_extractor  # needs the full requirements installed

    totals = dict(gold=0, found=0, extracted=0, kind_ok=0, false_tasks=0, tasks=0)
    for doc in docs:
        if use_classic:
            result = deadline_extractor.extract_deadlines(doc["text"], doc["name"])
        else:
            result = llm_extractor.extract_with_llm(doc["text"], doc["name"], config=cfg, today=today)

        gold = {g["date"]: g["kind"] for g in doc["gold"]}
        got = {d.dateIso: d for d in result.deadlines if d.dateIso}
        found = set(gold) & set(got)
        kind_ok = 0
        for iso in found:
            if (gold[iso] in ACTIONABLE_GOLD) == bool(got[iso].isActionable):
                kind_ok += 1
        false_tasks = [t for t in result.suggestedTasks if t.dueDate not in {
            iso for iso, kind in gold.items() if kind in ACTIONABLE_GOLD}]

        print(f"{doc['name']:<34} gold={len(gold)} found={len(found)} "
              f"extracted={len(got)} kinds_ok={kind_ok} false_tasks={len(false_tasks)}")
        totals["gold"] += len(gold)
        totals["found"] += len(found)
        totals["extracted"] += len(got)
        totals["kind_ok"] += kind_ok
        totals["false_tasks"] += len(false_tasks)
        totals["tasks"] += len(result.suggestedTasks)

    recall = totals["found"] / totals["gold"] if totals["gold"] else 1.0
    precision = totals["found"] / totals["extracted"] if totals["extracted"] else 1.0
    kinds = totals["kind_ok"] / totals["found"] if totals["found"] else 1.0
    print("-" * 70)
    print(f"date recall    {recall:6.1%}")
    print(f"date precision {precision:6.1%}")
    print(f"kind accuracy  {kinds:6.1%}")
    print(f"false tasks    {totals['false_tasks']} of {totals['tasks']} suggested")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--classic", action="store_true", help="evaluate the classic ML pipeline")
    parser.add_argument("--today", default=None, help="override today's date (YYYY-MM-DD)")
    args = parser.parse_args()
    today = date.fromisoformat(args.today) if args.today else date(2026, 11, 9)
    sys.exit(run(args.classic, today))
