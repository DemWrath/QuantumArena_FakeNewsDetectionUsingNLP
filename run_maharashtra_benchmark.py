"""
run_maharashtra_benchmark.py
TruthLens — Maharashtra News Benchmark Runner

Runs each sample through the full pipeline and produces:
  1. logs/maharashtra_benchmark_<timestamp>.json  — machine-readable full results
  2. logs/maharashtra_benchmark_<timestamp>.txt   — human-readable report card
  3. Console output with live progress

Usage:
  python run_maharashtra_benchmark.py
  python run_maharashtra_benchmark.py --ids MH-REAL-01 MH-FAKE-01   # run specific IDs
  python run_maharashtra_benchmark.py --category FAKE                # run one category
  python run_maharashtra_benchmark.py --quick                        # skip LIME explainability (faster)
  python run_maharashtra_benchmark.py --rpm 5                        # respect 5 req/min Gemini limit (default)
  python run_maharashtra_benchmark.py --no-throttle                  # skip inter-sample sleep (local/mock testing)
"""

import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# ── Project imports ────────────────────────────────────────────────────────────
# Adjust path so imports work when run from project root
sys.path.insert(0, str(Path(__file__).parent))

from maharashtra_test_set import MAHARASHTRA_NEWS_SAMPLES

# ── Logging setup ──────────────────────────────────────────────────────────────

LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_JSON = LOGS_DIR / f"maharashtra_benchmark_{_ts}.json"
LOG_TXT  = LOGS_DIR / f"maharashtra_benchmark_{_ts}.txt"

import io
_stdout_handler = logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace"))
_stdout_handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S"))
_file_handler = logging.FileHandler(LOGS_DIR / f"maharashtra_run_{_ts}.log", encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S"))
logging.basicConfig(
    level=logging.INFO,
    handlers=[_stdout_handler, _file_handler]
)
log = logging.getLogger("benchmark")


# ── Result dataclass (plain dict) ─────────────────────────────────────────────

def _empty_result(sample: dict) -> Dict[str, Any]:
    return {
        "id": sample["id"],
        "category": sample["category"],
        "expected": sample["expected"],
        "headline": sample["headline"],
        "elapsed_s": 0.0,
        "pipeline_output": None,
        "error": None,
        "verdict": {
            "predicted": None,
            "correct": None,              # bool
            "gemini_verdict": None,
            "confidence": None,
        },
        "metrics": {
            "fact_check": None,
            "emotion": None,
            "clickbait": None,
            "style": None,
        }
    }


# ── Pipeline wrapper ───────────────────────────────────────────────────────────

def run_single(sample: dict, quick: bool = False) -> Dict[str, Any]:
    """Run one sample through pipeline.execute_pipeline and return a result dict."""
    result = _empty_result(sample)
    t0 = time.perf_counter()

    try:
        # Lazy import so module-level singletons load only once
        from pipeline import execute_pipeline

        # Optionally patch out slow LIME explainability for quick runs
        if quick:
            import nlp_layer as _nl
            _orig = _nl._explainer.generate_explanation
            _nl._explainer.generate_explanation = lambda *a, **kw: {"skipped": "quick_mode"}

        output = execute_pipeline(
            text=sample["body"],
            headline=sample["headline"],
            url=None
        )

        if quick:
            _nl._explainer.generate_explanation = _orig

        result["pipeline_output"] = output
        elapsed = round(time.perf_counter() - t0, 2)
        result["elapsed_s"] = elapsed

        # ── Extract key signals ────────────────────────────────────────────────
        nlp = output.get("nlp_analysis", {})
        composite = nlp.get("composite_verdict", {})
        predicted = composite.get("final_label")

        result["verdict"]["predicted"] = predicted
        result["verdict"]["gemini_verdict"] = composite.get("gemini_verdict")
        result["verdict"]["confidence"] = composite.get("final_confidence")
        result["verdict"]["correct"] = (
            predicted == sample["expected"] if predicted else None
        )

        # Fact-check summary
        fc = nlp.get("fact_check", {})
        result["metrics"]["fact_check"] = {
            "verdict": fc.get("verdict"),
            "confidence": fc.get("confidence"),
            "search_grounded": fc.get("search_grounded", False),
            "sources": len(fc.get("grounding_sources", [])),
            "red_flags": fc.get("red_flags", []),
        }

        # Emotion summary
        em = nlp.get("emotional_tone", {})
        result["metrics"]["emotion"] = {
            "fear": em.get("fear"),
            "outrage": em.get("outrage"),
            "sensationalism": em.get("sensationalism"),
        }

        # Clickbait
        cb = nlp.get("clickbait_check", {})
        result["metrics"]["clickbait"] = {
            "is_clickbait": cb.get("is_clickbait"),
            "promise_fulfilled": cb.get("headline_promise_fulfilled"),
        }

        # Style classification
        sc = nlp.get("style_classification", {})
        result["metrics"]["style"] = {
            "label": sc.get("label"),
            "confidence": sc.get("confidence_score"),
        }

    except Exception as exc:
        result["elapsed_s"] = round(time.perf_counter() - t0, 2)
        result["error"] = str(exc)
        log.error(f"[{sample['id']}] Pipeline error: {exc}", exc_info=True)

    return result


# ── Report card renderer ────────────────────────────────────────────────────────

TICK = "[OK]"
CROSS = "[XX]"
LINE  = "-" * 72

def _icon(val: Optional[bool]) -> str:
    if val is True:  return TICK
    if val is False: return CROSS
    return "?"

def render_report(results: List[Dict], args: argparse.Namespace) -> str:
    """Build the human-readable .txt report."""
    lines = []
    lines.append("=" * 72)
    lines.append("  TruthLens — Maharashtra News Benchmark Report")
    lines.append(f"  Run at : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  Samples: {len(results)}")
    lines.append("=" * 72)
    lines.append("")

    correct = [r for r in results if r["verdict"]["correct"] is True]
    incorrect = [r for r in results if r["verdict"]["correct"] is False]
    errored = [r for r in results if r["error"]]
    skipped = [r for r in results if r["verdict"]["correct"] is None and not r["error"]]

    # ── Per-sample breakdown ───────────────────────────────────────────────────
    for r in results:
        v = r["verdict"]
        m = r["metrics"]
        icon = _icon(v["correct"])

        lines.append(LINE)
        lines.append(
            f"  [{icon}] {r['id']}  |  Category: {r['category']}"
            f"  |  Elapsed: {r['elapsed_s']}s"
        )
        lines.append(f"  Headline : {r['headline'][:80]}")

        if r["error"]:
            lines.append(f"  ERROR    : {r['error']}")
        else:
            lines.append(
                f"  Expected : {r['expected']:<12}  "
                f"Predicted: {v['predicted']:<12}  "
                f"Confidence: {v['confidence']}"
            )
            lines.append(
                f"  Gemini Verdict: {v['gemini_verdict']}"
            )

            # Fact-check
            fc = m.get("fact_check") or {}
            lines.append(
                f"  FactCheck: verdict={fc.get('verdict')}  "
                f"conf={fc.get('confidence')}  "
                f"search_grounded={fc.get('search_grounded')}  "
                f"sources={fc.get('sources')}"
            )
            rf = fc.get("red_flags", [])
            if rf:
                lines.append(f"  RedFlags : {'; '.join(rf[:3])}")

            # Emotion
            em = m.get("emotion") or {}
            lines.append(
                f"  Emotion  : fear={em.get('fear')}  "
                f"outrage={em.get('outrage')}  "
                f"sensat={em.get('sensationalism')}"
            )

            # Clickbait + Style
            cb = m.get("clickbait") or {}
            sc = m.get("style") or {}
            lines.append(
                f"  Clickbait: {cb.get('is_clickbait')}  |  "
                f"Style: {sc.get('label')} ({sc.get('confidence')})"
            )

        lines.append("")

    # ── Summary stats ──────────────────────────────────────────────────────────
    lines.append("=" * 72)
    lines.append("  SUMMARY")
    lines.append("=" * 72)

    total   = len(results)
    n_corr  = len(correct)
    n_incor = len(incorrect)
    n_err   = len(errored)

    accuracy = (n_corr / (n_corr + n_incor) * 100) if (n_corr + n_incor) > 0 else 0.0

    lines.append(f"  Total samples : {total}")
    lines.append(f"  Correct       : {n_corr}  ({accuracy:.1f}%)")
    lines.append(f"  Incorrect     : {n_incor}")
    lines.append(f"  Errors        : {n_err}")
    lines.append(f"  Skipped/None  : {len(skipped)}")

    # Per-category accuracy
    lines.append("")
    lines.append("  Per-category accuracy:")
    cats = sorted(set(r["category"] for r in results))
    for cat in cats:
        cat_results = [r for r in results if r["category"] == cat]
        cat_corr = [r for r in cat_results if r["verdict"]["correct"] is True]
        cat_total = len([r for r in cat_results if r["verdict"]["correct"] is not None])
        pct = (len(cat_corr) / cat_total * 100) if cat_total > 0 else 0.0
        lines.append(f"    {cat:<12} : {len(cat_corr)}/{cat_total}  ({pct:.0f}%)")

    # Timing
    elapsed_vals = [r["elapsed_s"] for r in results if r["elapsed_s"] > 0]
    if elapsed_vals:
        lines.append("")
        lines.append(f"  Avg elapsed  : {sum(elapsed_vals)/len(elapsed_vals):.1f}s")
        lines.append(f"  Max elapsed  : {max(elapsed_vals):.1f}s")
        lines.append(f"  Total elapsed: {sum(elapsed_vals):.1f}s")

    lines.append("")
    lines.append("  Incorrect predictions:")
    for r in incorrect:
        lines.append(
            f"    [{r['id']}]  expected={r['expected']}  "
            f"got={r['verdict']['predicted']}  "
            f"gemini={r['verdict']['gemini_verdict']}"
        )

    lines.append("=" * 72)
    return "\n".join(lines)


# ── CLI entrypoint ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run TruthLens pipeline against Maharashtra news test set."
    )
    parser.add_argument(
        "--ids", nargs="+", metavar="ID",
        help="Run only specific sample IDs (e.g. MH-REAL-01 MH-FAKE-02)"
    )
    parser.add_argument(
        "--category", choices=["REAL", "FAKE", "MISLEADING", "UNVERIFIED"],
        help="Run only samples matching this category"
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Skip LIME explainability to speed up the run"
    )
    parser.add_argument(
        "--no-save", action="store_true",
        help="Don't write output files (console only)"
    )
    parser.add_argument(
        "--rpm", type=int, default=5, metavar="N",
        help="Gemini requests-per-minute limit (default: 5 for free tier). "
             "Controls inter-sample sleep duration."
    )
    parser.add_argument(
        "--no-throttle", action="store_true",
        help="Disable inter-sample sleep (use for local/mock testing only)"
    )
    args = parser.parse_args()

    # Filter samples
    samples = MAHARASHTRA_NEWS_SAMPLES
    if args.ids:
        samples = [s for s in samples if s["id"] in args.ids]
    if args.category:
        samples = [s for s in samples if s["category"] == args.category]

    if not samples:
        log.error("No samples matched the given filters.")
        sys.exit(1)

    log.info(f"Starting Maharashtra benchmark — {len(samples)} sample(s), quick={args.quick}, rpm={args.rpm}")
    log.info(f"Output: {LOG_JSON}")

    # Each sample fires up to 3 Gemini calls (fact-check search, fact-check verdict, clickbait, emotion).
    # To stay inside N requests-per-minute, we need at least 60/N seconds between calls.
    # We use 3 calls/sample as conservative estimate and subtract time already spent.
    GEMINI_CALLS_PER_SAMPLE = 4  # search + verdict + clickbait + emotion
    throttle_window_s = (60.0 / args.rpm) * GEMINI_CALLS_PER_SAMPLE  # seconds to budget per sample

    results = []
    for i, sample in enumerate(samples, 1):
        log.info(f"[{i}/{len(samples)}] Running {sample['id']} ({sample['category']})...")
        result = run_single(sample, quick=args.quick)
        results.append(result)

        # Live console verdict
        v = result["verdict"]
        icon = _icon(v["correct"])
        status = "ERROR" if result["error"] else f"{v['predicted']} (expected {result['expected']})"
        log.info(f"  {icon} {sample['id']} -> {status}  ({result['elapsed_s']}s)")

        # ── Inter-sample rate-limit throttle ──────────────────────────────────
        if not args.no_throttle and i < len(samples):
            sleep_needed = max(0.0, throttle_window_s - result["elapsed_s"])
            if sleep_needed > 0:
                log.info(
                    f"  [throttle] Sleeping {sleep_needed:.0f}s to stay within "
                    f"{args.rpm} RPM (Gemini free-tier)..."
                )
                deadline = time.perf_counter() + sleep_needed
                while True:
                    remaining = deadline - time.perf_counter()
                    if remaining <= 0:
                        break
                    # Tick every second so the user can see progress
                    tick = min(remaining, 1.0)
                    time.sleep(tick)
                    remaining = deadline - time.perf_counter()
                    if remaining > 1.0:
                        log.info(f"  [throttle] {remaining:.0f}s remaining...")
                log.info("  [throttle] Done — resuming.")

    # ── Save JSON ──────────────────────────────────────────────────────────────
    if not args.no_save:
        with open(LOG_JSON, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "run_at": datetime.now().isoformat(),
                    "total_samples": len(results),
                    "results": results,
                },
                f,
                indent=2,
                ensure_ascii=False,
                default=str
            )
        log.info(f"JSON results saved -> {LOG_JSON}")

    # ── Render + save report ───────────────────────────────────────────────────
    report = render_report(results, args)
    # Write via the UTF-8-wrapped stdout handler to avoid Windows cp1252 crash
    _stdout_handler.stream.write("\n" + report + "\n")
    _stdout_handler.stream.flush()

    if not args.no_save:
        LOG_TXT.write_text(report, encoding="utf-8")
        log.info(f"Text report saved -> {LOG_TXT}")

    # Exit code: non-zero if there were errors
    n_errors = len([r for r in results if r["error"]])
    sys.exit(1 if n_errors else 0)


if __name__ == "__main__":
    main()
