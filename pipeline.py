import argparse
import sys
import json

from input_handler import fetch_text, extract_claim_evidence
from sentence_level_media_bias_naacl_2024.sentence_level_media_bias_naacl_2024.bias_event_relation_graph_BASIL import analyze_bias_for_text
from nlp_layer import run_nlp_layers
from scraper_layer import SourceIntelligenceTracker

# Initialize global cache tracker
source_tracker = SourceIntelligenceTracker()


def execute_pipeline(text: str, headline: str = None, url: str = None) -> dict:
    """Run all analysis layers on resolved text."""
    # 1. Run Transformer NLP Layer (DistilBERT + Gemini)
    print("Running NLP & Style Analysis Layer...")
    nlp_result = run_nlp_layers(text, headline)

    # 2. Run Event Relation Bias Graph (NAACL 2024)
    print("Running Media Bias Event Relation Graph Analysis...")
    bias_result = analyze_bias_for_text(text)
    
    # 3. Source Intelligence (Scrapers + Cache)
    print("Evaluating Source Reputation...")
    source_intel = source_tracker.get_domain_info(url)

    return {
        "source_intelligence": source_intel,
        "nlp_analysis": nlp_result,
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
    
    # Optional explicitly provided headline (if text is used instead of URL)
    parser.add_argument(
        "--headline", type=str,
        help="Optional explicitly provided headline for clickbait checking (useful with --text)."
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
        
    resolved_headline = input_data.get("title", args.headline)

    print(f"Executing pipeline on text ({len(resolved_text)} chars)...")

    # Extract claim/evidence structure
    claim_evidence = extract_claim_evidence(input_data)

    # Run analysis layers
    layers = execute_pipeline(resolved_text, headline=resolved_headline, url=input_data.get("url", "raw_text"))

    # Construct unified output
    output = {
        "input_source": input_data.get("url", "raw_text"),
        "input_title": resolved_headline,
        "input_text": resolved_text,
        "claim_evidence": claim_evidence,
        "layers": layers
    }

    print("\n--- PIPELINE RESULT ---")
    print(json.dumps(output, indent=2))
