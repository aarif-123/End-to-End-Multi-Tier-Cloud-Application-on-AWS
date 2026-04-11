from fastapi import FastAPI, HTTPException
import mysql.connector
from mysql.connector import Error
import os
import boto3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Tier Cloud Application")

# Config
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'admin')
DB_PASS = os.environ.get('DB_PASS', 'password123')
DB_NAME = os.environ.get('DB_NAME', 'intern_db')
S3_BUCKET = os.environ.get('S3_BUCKET', 'intern-project-assets')


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        return conn
    except Error as e:
        logger.error(f"Database connection failed: {e}")
        return None


def check_s3_access():
    try:
        s3 = boto3.client('s3')
        # Check basic access
        s3.list_objects_v2(Bucket=S3_BUCKET, MaxKeys=1)
        return True
    except Exception as e:
        logger.debug(f"S3 access check failed: {e}")
        return False


@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Cloud Application API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    db_conn = get_db_connection()
    db_status = "connected" if db_conn else "disconnected"
    s3_status = "accessible" if check_s3_access() else "inaccessible"
    
    if db_conn:
        db_conn.close()

    status = "healthy" if db_status == "connected" else "unhealthy"
    
    result = {
        "database": db_status,
        "s3_storage": s3_status,
        "status": status
    }
    
    if status == "unhealthy":
        logger.error(f"Health check failed: {result}")
        raise HTTPException(status_code=500, detail=result)
        
    return result

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting application on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
