"""
run_benchmark.py
TruthLens — Generalized News Benchmark Runner

Runs any test set through the full pipeline and produces:
  1. logs/<dataset>_benchmark_<timestamp>.json  — machine-readable full results
  2. logs/<dataset>_benchmark_<timestamp>.txt   — human-readable report card
  3. Console output with live progress

Usage:
  python run_benchmark.py --dataset politics
  python run_benchmark.py --dataset maharashtra
  python run_benchmark.py --dataset politics --ids POL-REAL-01 POL-FAKE-01
  python run_benchmark.py --dataset politics --category FAKE
  python run_benchmark.py --dataset politics --quick
  python run_benchmark.py --dataset politics --rpm 5
  python run_benchmark.py --dataset politics --no-throttle
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
sys.path.insert(0, str(Path(__file__).parent))

# Dataset registry — maps --dataset name to (module, variable)
DATASETS = {
    "maharashtra": ("maharashtra_test_set", "MAHARASHTRA_NEWS_SAMPLES"),
    "politics":    ("politics_test_set",    "POLITICS_NEWS_SAMPLES"),
}

# ── Logging setup ──────────────────────────────────────────────────────────────

LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


def _setup_logging(dataset_name: str):
    """Create per-run log files and configure logging."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_json = LOGS_DIR / f"{dataset_name}_benchmark_{ts}.json"
    log_txt  = LOGS_DIR / f"{dataset_name}_benchmark_{ts}.txt"
    log_file = LOGS_DIR / f"{dataset_name}_run_{ts}.log"

    import io
    stdout_handler = logging.StreamHandler(
        io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    )
    stdout_handler.setFormatter(
        logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")
    )
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")
    )

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # Clear any existing handlers from previous runs
    for h in root.handlers[:]:
        root.removeHandler(h)
    root.addHandler(stdout_handler)
    root.addHandler(file_handler)

    return log_json, log_txt, stdout_handler


# ── Result dict ───────────────────────────────────────────────────────────────

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
            "correct": None,
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
    log = logging.getLogger("benchmark")
    result = _empty_result(sample)
    t0 = time.perf_counter()

    try:
        from pipeline import execute_pipeline

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
LINE = "-" * 72

def _icon(val: Optional[bool]) -> str:
    if val is True:  return TICK
    if val is False: return CROSS
    return "?"

def render_report(results: List[Dict], dataset_name: str) -> str:
    """Build the human-readable .txt report."""
    pretty_name = dataset_name.replace("_", " ").title()
    lines = []
    lines.append("=" * 72)
    lines.append(f"  TruthLens — {pretty_name} News Benchmark Report")
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
        description="Run TruthLens pipeline against a news benchmark test set."
    )
    parser.add_argument(
        "--dataset", required=True, choices=list(DATASETS.keys()),
        help="Which test set to run (e.g. politics, maharashtra)"
    )
    parser.add_argument(
        "--ids", nargs="+", metavar="ID",
        help="Run only specific sample IDs (e.g. POL-REAL-01 POL-FAKE-02)"
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

    # ── Load dataset dynamically ──────────────────────────────────────────────
    mod_name, var_name = DATASETS[args.dataset]
    import importlib
    mod = importlib.import_module(mod_name)
    samples = getattr(mod, var_name)

    # ── Setup logging ─────────────────────────────────────────────────────────
    log_json, log_txt, stdout_handler = _setup_logging(args.dataset)
    log = logging.getLogger("benchmark")

    # Filter samples
    if args.ids:
        samples = [s for s in samples if s["id"] in args.ids]
    if args.category:
        samples = [s for s in samples if s["category"] == args.category]

    if not samples:
        log.error("No samples matched the given filters.")
        sys.exit(1)

    log.info(f"Starting {args.dataset} benchmark — {len(samples)} sample(s), quick={args.quick}, rpm={args.rpm}")
    log.info(f"Output: {log_json}")

    GEMINI_CALLS_PER_SAMPLE = 4
    throttle_window_s = (60.0 / args.rpm) * GEMINI_CALLS_PER_SAMPLE

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
                    tick = min(remaining, 1.0)
                    time.sleep(tick)
                    remaining = deadline - time.perf_counter()
                    if remaining > 1.0:
                        log.info(f"  [throttle] {remaining:.0f}s remaining...")
                log.info("  [throttle] Done — resuming.")

    # ── Save JSON ──────────────────────────────────────────────────────────────
    if not args.no_save:
        with open(log_json, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "dataset": args.dataset,
                    "run_at": datetime.now().isoformat(),
                    "total_samples": len(results),
                    "results": results,
                },
                f,
                indent=2,
                ensure_ascii=False,
                default=str
            )
        log.info(f"JSON results saved -> {log_json}")

    # ── Render + save report ───────────────────────────────────────────────────
    report = render_report(results, args.dataset)
    stdout_handler.stream.write("\n" + report + "\n")
    stdout_handler.stream.flush()

    if not args.no_save:
        log_txt.write_text(report, encoding="utf-8")
        log.info(f"Text report saved -> {log_txt}")

    # Exit code: non-zero if there were errors
    n_errors = len([r for r in results if r["error"]])
    sys.exit(1 if n_errors else 0)


if __name__ == "__main__":
    main()
