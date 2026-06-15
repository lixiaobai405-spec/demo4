"""
Flask App — Leadership Modeling AI Agent
Serves frontend + proxies DeepSeek API calls.
"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from backend.config import MAX_UPLOAD_SIZE, ALLOWED_EXTENSIONS
from backend.ai_service import (
    chat,
    analyze_document,
    generate_dimensions,
    generate_descriptions,
    generate_anchors,
    regenerate,
)

app = Flask(__name__, static_folder=None)
CORS(app)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")


# ── Static File Routes ──────────────────────────────────────────

@app.route("/")
def root():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def serve_frontend(filename):
    if os.path.exists(os.path.join(FRONTEND_DIR, filename)):
        return send_from_directory(FRONTEND_DIR, filename)
    return jsonify({"error": "Not found"}), 404


# ── API Routes ──────────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Step1: AI guided dialogue"""
    data = request.get_json()
    if not data or "messages" not in data:
        return jsonify({"error": "messages required"}), 400

    messages = data["messages"]
    context = data.get("context", "")
    try:
        reply = chat(messages, context)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze-doc", methods=["POST"])
def api_analyze_doc():
    """Step1: Document analysis"""
    if "file" not in request.files:
        return jsonify({"error": "file required"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "no file selected"}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"unsupported file type: {ext}"}), 400

    try:
        content = file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            return jsonify({"error": "file too large (max 10MB)"}), 400

        text = ""
        if ext in ("txt", "md"):
            text = content.decode("utf-8", errors="replace")
        elif ext == "pdf":
            text = f"[PDF document: {file.filename}] — PDF text extraction requires additional library"
        elif ext in ("docx", "doc"):
            text = f"[DOCX document: {file.filename}] — DOCX text extraction requires additional library"

        if not text.strip():
            text = f"[Empty or unreadable file: {file.filename}]"

        result = analyze_document(text, file.filename)
        return jsonify({"result": result, "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-dimensions", methods=["POST"])
def api_generate_dimensions():
    """Step2: Generate leadership dimensions"""
    data = request.get_json()
    if not data or "company_info" not in data:
        return jsonify({"error": "company_info required"}), 400

    company_info = data["company_info"]
    level = data.get("level", "中层管理者")
    try:
        result = generate_dimensions(company_info, level)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-descriptions", methods=["POST"])
def api_generate_descriptions():
    """Step3: Generate dimension descriptions"""
    data = request.get_json()
    if not data or "dimensions" not in data:
        return jsonify({"error": "dimensions required"}), 400

    dimensions = data["dimensions"]
    company_info = data.get("company_info", "")
    level = data.get("level", "中层管理者")
    try:
        result = generate_descriptions(json.dumps(dimensions, ensure_ascii=False), company_info, level)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-anchors", methods=["POST"])
def api_generate_anchors():
    """Step4: Generate BARS behavior anchors"""
    data = request.get_json()
    if not data or "dimensions" not in data:
        return jsonify({"error": "dimensions required"}), 400

    dimensions = data["dimensions"]
    company_info = data.get("company_info", "")
    level = data.get("level", "中层管理者")
    try:
        result = generate_anchors(json.dumps(dimensions, ensure_ascii=False), company_info, level)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/regenerate", methods=["POST"])
def api_regenerate():
    """Regenerate a single item"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "request body required"}), 400

    original = data.get("original", "")
    direction = data.get("direction", "优化表述")
    item_type = data.get("item_type", "定位描述")
    try:
        result = regenerate(original, direction, item_type)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Main ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Frontend directory: {FRONTEND_DIR}")
    print("Starting server at http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)
