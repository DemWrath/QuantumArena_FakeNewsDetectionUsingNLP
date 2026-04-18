"""
app.py
TruthLens Flask API

Single endpoint: POST /api/analyze
Accepts { url?, text? } → runs the full pipeline → returns flat JSON.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pipeline import execute_pipeline
from input_handler import fetch_text
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/')
def serve_frontend():
    return send_file('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json(force=True, silent=True) or {}
        url = data.get('url', '').strip()
        text = data.get('text', '').strip()

        if not url and not text:
            return jsonify({"error": "No input supplied. Provide 'url' or 'text'."}), 400

        # URL takes priority; raw text falls back
        source = url if url else text
        input_data = fetch_text(source)

        if input_data.get("type") == "error":
            return jsonify({"error": f"Failed to fetch input: {input_data.get('message')}"}), 400

        resolved_text = input_data.get("text", "")
        if not resolved_text.strip():
            return jsonify({"error": "No text content could be extracted from input."}), 400

        resolved_headline = input_data.get("title", "")

        # Run all analysis layers
        layers = execute_pipeline(
            resolved_text,
            headline=resolved_headline,
            url=input_data.get("url", None)
        )

        # Flat response — frontend reads keys directly from `data`
        return jsonify({
            "input_source": input_data.get("url", "raw_text"),
            "input_title": resolved_headline,
            "nlp_analysis": layers["nlp_analysis"],
            "media_bias": layers["media_bias"],
            "source_intelligence": layers["source_intelligence"],
        }), 200

    except Exception as e:
        app.logger.error(f"Pipeline failure: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
