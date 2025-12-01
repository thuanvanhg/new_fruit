# HƯỚNG DẪN SỬ DỤNG API `new_fruit`

## 1. Môi trường & Biến môi trường

Cần cấu hình các biến môi trường (Render, hoặc `.env` khi chạy local):

- `NEO4J_URI` – ví dụ: `bolt://neo4j:7687` hoặc URI Aura
- `NEO4J_USER`
- `NEO4J_PASSWORD`
- `MONGO_URI` – ví dụ: chuỗi kết nối MongoDB Atlas
- `MONGO_DB_NAME` – ví dụ: `new_fruit`

## 2. Chạy local

```bash
pip install -r requirements.txt
export NEO4J_URI=...
export NEO4J_USER=...
export NEO4J_PASSWORD=...
export MONGO_URI=...
export MONGO_DB_NAME=new_fruit

python api/app.py
