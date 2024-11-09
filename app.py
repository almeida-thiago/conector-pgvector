import os
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash
from sentence_transformers import SentenceTransformer
from psycopg2 import pool
import threading
import io
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
auth = HTTPBasicAuth()

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
password_hash = generate_password_hash(password)
users = {username: password_hash}

@auth.verify_password
def verify_password(user, password):
    if user in users and check_password_hash(users.get(user), password):
        return user

model = SentenceTransformer('all-mpnet-base-v2') # testar outrpos modelos

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
db_pool = pool.SimpleConnectionPool(
    1, 10,
    host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
)

with db_pool.getconn() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS qa_data (
                id SERIAL PRIMARY KEY,
                question TEXT,
                answer TEXT,
                embedding vector(768)
            );
        """)
        conn.commit()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_embeddings_from_csv(data):
    embeddings = []
    for question, answer in data:
        embedding = model.encode(f"{question.strip()} {answer.strip()}")
        embeddings.append(embedding)
    
    with db_pool.getconn() as conn:
        with conn.cursor() as cur:
            for i, (question, answer) in enumerate(data):
                embedding_array = embeddings[i].tolist()
                cur.execute("""
                    INSERT INTO qa_data (question, answer, embedding)
                    VALUES (%s, %s, %s);
                """, (question, answer, embedding_array))
            conn.commit()
        db_pool.putconn(conn)
    logger.info("Embeddings generated and data inserted successfully")

def handle_file_processing(file):
    try:
        file_stream = io.BytesIO(file.read())
        df = pd.read_csv(file_stream)

        if 'question' not in df.columns or 'answer' not in df.columns:
            logger.error("CSV must contain 'question' and 'answer' columns")
            return

        data = df[['question', 'answer']].values.tolist()
        generate_embeddings_from_csv(data)
        
        logger.info("CSV processed and embeddings generated successfully")
    
    except Exception as e:
        logger.exception("Error while processing the CSV file")

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_csv():
    file = request.files.get('file')
    if not file:
        logger.error("No file provided")
        return jsonify({"error": "No file provided"}), 400
    
    threading.Thread(target=handle_file_processing, args=(file,)).start()
    
    logger.info("File uploaded successfully, processing started in the background")
    return jsonify({"message": "File uploaded successfully. Processing is running in the background."}), 202

@app.route('/search', methods=['POST'])
@auth.login_required
def search_vectors():
    data = request.json
    query = data.get('question')
    if not query:
        logger.error("No query provided")
        return jsonify({"error": "No query provided"}), 400

    k = data.get('offset', 5)
    query_vector = model.encode(query).reshape(1, -1).astype(np.float32)
    query_vector_list = query_vector.flatten().tolist()

    try:
        with db_pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, question, answer, embedding <=> %s::vector AS distance
                    FROM qa_data
                    ORDER BY distance
                    LIMIT %s;
                """, (query_vector_list, k))
                
                rows = cur.fetchall()
                
                results = [{"id": row[0], "distance": row[3], "question": row[1], "answer": row[2]} for row in rows]
                db_pool.putconn(conn)

        if not results:
            logger.warning("No results found after database query.")
            return jsonify({"message": "No results found"}), 404

        return jsonify({"results": results})
    
    except Exception as e:
        logger.exception("Error during vector search")
        return jsonify({"error": "Error during vector search"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
