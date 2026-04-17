from flask import Flask, request, jsonify
from flask_cors import CORS
from pipeline import execute_pipeline
from input_handler import fetch_text, extract_claim_evidence
import os
import traceback

app = Flask(__name__)
CORS(app)  # Enable cross-origin for local UI testing

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json(force=True, silent=True) or {}
        url = data.get('url', '').strip()
        text = data.get('text', '').strip()

        if not url and not text:
            return jsonify({"error": "No threat payload supplied. Provide URL or Text."}), 400

        # Treat source as url primarily if provided
        source = url if url else text
        
        # 1. Fetch Input (Using existing robust input_handler)
        input_data = fetch_text(source)
        if input_data.get("type") == "error":
            return jsonify({"error": f"Failed to fetch input: {input_data.get('message')}"}), 400

        resolved_text = input_data.get("text", "")
        if not resolved_text.strip():
            return jsonify({"error": "No text content could be extracted from input."}), 400

        resolved_headline = input_data.get("title", "")
        
        # Extract general claims mapping (if needed downstream)
        claim_evidence = extract_claim_evidence(input_data)

        # 2. Execute Master Pipeline (Transformers, Scraping, Graphing)
        layers = execute_pipeline(
            resolved_text, 
            headline=resolved_headline, 
            url=input_data.get("url", None)
        )

        # 3. Formulate Output
        output = {
            "input_source": input_data.get("url", "raw_text"),
            "input_title": resolved_headline,
            "input_text": resolved_text,
            "claim_evidence": claim_evidence,
            "layers": layers
        }
        
        return jsonify(output), 200

    except Exception as e:
        app.logger.error(f"Pipeline failure: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Execute Locally on Port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
