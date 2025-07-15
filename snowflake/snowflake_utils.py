import json
from snowflake.connector import connect
import os
from datetime import datetime,timezone
from dotenv import load_dotenv
import uuid
load_dotenv()

# Setup Snowflake connection
def get_snowflake_connection():
    return connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

def store_chunks_in_snowflake(user_id, collection_name, chunks, embeddings):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    
    try:
        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = str(uuid.uuid4())
            embedding_json = json.dumps(embedding.tolist() if hasattr(embedding, 'tolist') else embedding)
            cursor.execute("""
                INSERT INTO RAG_QA.PDF_DATA.PDF_CHUNKS (ID, USER_ID, COLLECTION_NAME, CHUNK, EMBEDDING)
                VALUES (%s, %s, %s, %s, %s)
            """, (chunk_id, user_id, collection_name, chunk, embedding_json))
        
        conn.commit()
        print(f"Successfully inserted {len(chunks)} chunks into Snowflake")
    except Exception as e:
        print("Error inserting into Snowflake:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
def log_query_response(user_id, collection_name, question, chunks_text,  response):
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        log_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            INSERT INTO RAG_QA.PDF_DATA.QUERY_LOGS (
                ID, USER_ID, COLLECTION_NAME, QUESTION, RETRIEVED_CHUNKS,  RESPONSE, TIMESTAMP
            )
            VALUES (%s, %s, %s,  %s, %s,  %s, %s)
        """, (
            log_id,
            user_id,
            collection_name,
            question,
            chunks_text,
            response,
            timestamp
        ))

        conn.commit()
        print(" Logged query and response in Snowflake.")
    except Exception as e:
        print(" Failed to log query:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()