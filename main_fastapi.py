import os
from fastapi import FastAPI, HTTPException
import mysql.connector
import random
import socket
import time
from contextlib import asynccontextmanager

# Proxy server

default_read_query = "SELECT * FROM store WHERE store_id = 1"
default_write_query = f"INSERT INTO testing_table (number) VALUES (500)"

# Fetch IPs from environment variables
MANAGER_DB = {
    "host": os.getenv("MANAGER_IP"),
    "user": "replicator",
    "password": "",
    "database": "sakila"
}
WORKER_DBS = [
    {"host": os.getenv("WORKER1_IP"), "user": "replicator", "password": "", "database": "sakila"},
    {"host": os.getenv("WORKER2_IP"), "user": "replicator", "password": "", "database": "sakila"}
]

# Helper function to connect to MySQL and execute a query
def execute_query(db_config, query):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(query)

        # Determine if it’s a SELECT or non-SELECT query
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
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    query = "CREATE TABLE IF NOT EXISTS testing_table (id INT PRIMARY KEY AUTO_INCREMENT, number INT);"
    try:
        execute_query(MANAGER_DB, query)
        print("Table 'testing_table' ensured on startup.")
    except HTTPException as e:
        print(f"Failed to create table on startup: {e.detail}")
    
    yield  # Allow the application to start up

app = FastAPI(lifespan=lifespan)

# Routing Strategy 1: Direct Hit (sends all write requests to manager)
@app.post("/write")
def write_direct():
    affected_rows = execute_query(MANAGER_DB, default_write_query)
    return {"status": "success", "affected_rows": affected_rows, "role": "manager", "ip": MANAGER_DB["host"]}  # Return the count of affected rows

# Routing Strategy 1: Direct Hit for reading (sends all read requests to manager)
@app.get("/read/direct")
def read_direct():
    result = execute_query(MANAGER_DB, default_read_query)
    return {"status": "success", "data": result, "role": "manager", "ip": MANAGER_DB["host"]}

# Routing Strategy 2: Random (sends read requests to a random worker)
@app.get("/read/random")
def read_random():
    worker_db = random.choice(WORKER_DBS)
    result = execute_query(worker_db, default_read_query)
    return {"status": "success", "data": result, "role": "worker", "ip": worker_db["host"]}

# Routing Strategy 3: Customized (sends read to the lowest latency worker)
def measure_latency(host):
    start = time.time()
    try:
        socket.create_connection((host, 3306), timeout=1)
    except socket.timeout:
        return float('inf')
    return time.time() - start

@app.get("/read/customized")
def read_customized():
    # Measure latency and select the worker with the lowest latency
    latencies = [(db, measure_latency(db["host"])) for db in WORKER_DBS]
    best_db = min(latencies, key=lambda x: x[1])[0]
    result = execute_query(best_db, default_read_query)
    return {"status": "success", "data": result, "role": "worker", "ip": best_db["host"]}

# Testing endpoint for initial connectivity
@app.get("/")
def root():
    return {"message": "Proxy server is running"}
