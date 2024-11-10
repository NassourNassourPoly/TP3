import os
from fastapi import FastAPI, HTTPException
import mysql.connector
import random
import socket
import time

app = FastAPI()

# Fetch IPs from environment variables
MANAGER_DB = {
    "host": os.getenv("MANAGER_IP"),
    "user": "root",
    "password": "",
    "database": "sakila"
}
WORKER_DBS = [
    {"host": os.getenv("WORKER1_IP"), "user": "root", "password": "", "database": "sakila"},
    {"host": os.getenv("WORKER2_IP"), "user": "root", "password": "", "database": "sakila"}
]

# Helper function to connect to MySQL and execute a query
def execute_query(db_config, query):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(query)

        # Check if it’s a SELECT or non-SELECT query to fetch results or commit changes
        if query.strip().lower().startswith("select"):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount  # Number of affected rows for non-SELECT queries

        cursor.close()
        conn.close()
        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

# Routing Strategy 1: Direct Hit (sends all to manager)
@app.post("/write")
def write_direct(query: str):
    result = execute_query(MANAGER_DB, query)
    return {"status": "success", "affected_rows": result}  # For non-SELECT queries

@app.get("/read/direct")
def read_direct(query: str):
    result = execute_query(MANAGER_DB, query)
    return {"status": "success", "data": result}

# Routing Strategy 2: Random (sends read to random worker)
@app.get("/read/random")
def read_random(query: str):
    worker_db = random.choice(WORKER_DBS)
    result = execute_query(worker_db, query)
    return {"status": "success", "data": result}

# Routing Strategy 3: Customized (sends read to the lowest latency worker)
def measure_latency(host):
    start = time.time()
    try:
        socket.create_connection((host, 3306), timeout=1)
    except socket.timeout:
        return float('inf')
    return time.time() - start

@app.get("/read/optimized")
def read_optimized(query: str):
    # Measure latency and select the worker with the lowest latency
    latencies = [(db, measure_latency(db["host"])) for db in WORKER_DBS]
    best_db = min(latencies, key=lambda x: x[1])[0]
    result = execute_query(best_db, query)
    return {"status": "success", "data": result}

# Testing endpoint for initial connectivity
@app.get("/")
def root():
    return {"message": "Proxy server is running"}
