import argparse
import sys
import json
import os

from input_handler import fetch_text, extract_claim_evidence
from Fake_News_Detection.Fake_News_Detection.classifier import run_classification
from sentence_level_media_bias_naacl_2024.sentence_level_media_bias_naacl_2024.bias_event_relation_graph_BASIL import analyze_bias_for_text


def execute_pipeline(text: str) -> dict:
    """Run all analysis layers on resolved text."""
    # 1. Run Fake News Detection ML classification
    print("Running Fake News Classification Layer...")
    ml_result = run_classification(text)

    # 2. Run Event Relation Bias Graph (NAACL 2024)
    print("Running Media Bias Event Relation Graph Analysis...")
    bias_result = analyze_bias_for_text(text)

    return {
        "ml_classification": ml_result,
        "media_bias": bias_result
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Multi-layered Media Analysis Pipeline"
    )

    # Mutually exclusive: --text or --url
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--text", type=str,
        help="Raw text statement to analyze."
    )
    input_group.add_argument(
        "--url", type=str,
        help="URL of an article to fetch and analyze."
    )

    args = parser.parse_args()

    # Resolve input via unified handler
    source = args.url if args.url else args.text
    print(f"Resolving input: '{source[:60]}...' " if len(source) > 60 else f"Resolving input: '{source}'")

    input_data = fetch_text(source)

    if input_data["type"] == "error":
        print(f"\n[ERROR] Failed to fetch input: {input_data['message']}", file=sys.stderr)
        sys.exit(1)

    resolved_text = input_data.get("text", "")
    if not resolved_text.strip():
        print("[ERROR] No text content could be extracted from the input.", file=sys.stderr)
        sys.exit(1)

    print(f"Executing pipeline on text ({len(resolved_text)} chars)...")

    # Extract claim/evidence structure
    claim_evidence = extract_claim_evidence(input_data)

    # Run analysis layers
    layers = execute_pipeline(resolved_text)

    # Construct unified output
    output = {
        "input_source": input_data.get("url", "raw_text"),
        "input_title": input_data.get("title", None),
        "input_text": resolved_text,
        "claim_evidence": claim_evidence,
        "layers": layers
    }

    print("\n--- PIPELINE RESULT ---")
    print(json.dumps(output, indent=2))
