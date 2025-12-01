import os
from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from pymongo import MongoClient

# ================== CẤU HÌNH KẾT NỐI ==================

NEO4J_URI = os.environ.get("NEO4J_URI", "")
NEO4J_USER = os.environ.get("NEO4J_USER", "")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "new_fruit")

# Neo4j driver (có thể None nếu chưa cấu hình)
neo4j_driver = None
if NEO4J_URI and NEO4J_USER and NEO4J_PASSWORD:
    neo4j_driver = GraphDatabase.driver(NEO4J_URI,
                                        auth=(NEO4J_USER, NEO4J_PASSWORD))

# MongoDB client
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB_NAME]

# ================== TẠO APP FLASK ==================

app = Flask(__name__)


@app.get("/")
def index():
    """Trang kiểm tra nhanh API."""
    return jsonify({"message": "new_fruit API đang chạy"})


@app.get("/health")
def health():
    """Kiểm tra kết nối Neo4j & MongoDB."""
    status = {}

    # Check MongoDB
    try:
        collections = mongo_db.list_collection_names()
        status["mongo"] = {"ok": True, "collections": collections}
    except Exception as e:
        status["mongo"] = {"ok": False, "error": str(e)}

    # Check Neo4j
    if neo4j_driver is None:
        status["neo4j"] = {
            "ok": False,
            "error": "Chưa cấu hình NEO4J_URI/USER/PASSWORD"
        }
    else:
        try:
            with neo4j_driver.session() as session:
                result = session.run("RETURN 1 AS ok").single()
                status["neo4j"] = {"ok": True, "result": result["ok"]}
        except Exception as e:
            status["neo4j"] = {"ok": False, "error": str(e)}

    return jsonify(status)


@app.get("/search")
def search():
    """
    Tìm kiếm trái cây.
    - query Neo4j theo tên trái cây
    - có thể mở rộng truy vấn MongoDB nếu cần
    Gọi dạng: /search?query=buoi
    """
    q = (request.args.get("query") or "").strip()
    if not q:
        return jsonify({"error": "Thiếu tham số 'query'"}), 400

    results = {"query": q, "neo4j": [], "mongo": []}

    # -------- Tìm trong Neo4j --------
    if neo4j_driver is not None:
        cypher = """
        MATCH (f:Fruit)
        WHERE toLower(f.name) CONTAINS toLower($q)
           OR toLower(coalesce(f.label_vi, '')) CONTAINS toLower($q)
        RETURN f LIMIT 20
        """
        try:
            with neo4j_driver.session() as session:
                for record in session.run(cypher, q=q):
                    node = record["f"]
                    results["neo4j"].append(dict(node))
        except Exception as e:
            results["neo4j_error"] = str(e)

    # -------- Tìm trong MongoDB (nếu có collection 'products') --------
    try:
        if "products" in mongo_db.list_collection_names():
            cursor = mongo_db["products"].find(
                {"name": {"$regex": q, "$options": "i"}},
                {"_id": 0}
            ).limit(20)
            results["mongo"] = list(cursor)
    except Exception as e:
        results["mongo_error"] = str(e)

    return jsonify(results)


# Cho Render / gunicorn gọi
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
