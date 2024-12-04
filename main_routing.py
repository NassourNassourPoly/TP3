import os
from fastapi import FastAPI, Request, HTTPException
import httpx

# Gatekeeper + Trusted host server
app = FastAPI()

# The new server to which requests will be forwarded
NEW_SERVER_URL = f"http://{os.getenv("ROUTE_IP")}:8000"

def forward_request(endpoint: str, method: str):
    url = f"{NEW_SERVER_URL}{endpoint}"
    with httpx.Client() as client:
        try:
            if method.lower() == "get":
                response = client.get(url)
            elif method.lower() == "post":
                response = client.post(url)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")

            # Return the response from the new server
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to forward request: {e}")

@app.post("/write")
def write_direct():
    return forward_request("/write", "post")

@app.get("/read/direct")
def read_direct():
    return forward_request("/read/direct", "get")

@app.get("/read/random")
def read_random():
    return forward_request("/read/random", "get")

@app.get("/read/customized")
def read_customized():
    return forward_request("/read/customized", "get")

# Testing endpoint for initial connectivity
@app.get("/")
def root():
    return {"message": "I am running"}
