import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from search import search

DEFAULT_PORT = 5001

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ]
        }
    },
)


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.get("/search")
def search_endpoint():
    query = request.args.get("q", "")
    limit = request.args.get("limit", default=10, type=int)
    return jsonify({"results": search(query, limit=limit)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    app.run(host="127.0.0.1", port=port, debug=True)
