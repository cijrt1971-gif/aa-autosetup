from flask import Flask, jsonify, request, send_from_directory
import json, pathlib

BASE = pathlib.Path(__file__).resolve().parent
UI_TEMPLATES = BASE / "ui_templates"
CORE = UI_TEMPLATES / "core"
CUSTOM = UI_TEMPLATES / "custom"
CUSTOM.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=str(BASE / "static"), static_url_path="/static")

def load_templates():
    out = []
    for p in sorted(CORE.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf8"))
            data["_source"] = "core"
            data["_filename"] = p.name
            out.append(data)
        except Exception:
            continue
    for p in sorted(CUSTOM.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf8"))
            data["_source"] = "custom"
            data["_filename"] = p.name
            out.append(data)
        except Exception:
            continue
    return out

@app.route("/ui-templates", methods=["GET"])
def ui_templates():
    return jsonify(load_templates())

@app.route("/ui-templates/upload", methods=["POST"])
def upload_template():
    if not request.is_json:
        return jsonify({"error":"expected application/json"}), 400
    data = request.get_json()
    if "id" not in data or "components" not in data:
        return jsonify({"error":"manifest must include id and components"}), 400
    tid = "".join(c for c in data["id"] if c.isalnum() or c in ("-","_")).strip()
    if not tid:
        from uuid import uuid4
        tid = str(uuid4())[:8]
    outp = CUSTOM / f"{tid}.json"
    outp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")
    return jsonify({"saved": str(outp.name)}), 201

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    static_dir = BASE / "static"
    index = static_dir / "index.html"
    if path == "" and index.exists():
        return send_from_directory(str(static_dir), "index.html")
    if path and (static_dir / path).exists():
        return send_from_directory(str(static_dir), path)
    return "AA backend running. Endpoints: GET /ui-templates , POST /ui-templates/upload", 200

if __name__ == "__main__":
    print("Starting Flask backend on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
