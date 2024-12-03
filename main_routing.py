import os
from fastapi import FastAPI, Request, HTTPException
import httpx

# Proxy server
app = FastAPI()

# The new server to which requests will be forwarded
NEW_SERVER_URL = f"http://{os.getenv("ROUTE_IP")}:8000"

async def forward_request(endpoint: str, method: str, data: dict = None):
    url = f"{NEW_SERVER_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        try:
            if method.lower() == "get":
                response = await client.get(url)
            elif method.lower() == "post":
                response = await client.post(url, json=data)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")

            # Return the response from the new server
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to forward request: {e}")

@app.post("/write")
async def write_direct():
    return await forward_request("/write", "post")

@app.get("/read/direct")
async def read_direct():
    return await forward_request("/read/direct", "get")

@app.get("/read/random")
async def read_random():
    return await forward_request("/read/random", "get")

@app.get("/read/customized")
async def read_customized():
    return await forward_request("/read/customized", "get")

# Testing endpoint for initial connectivity
@app.get("/")
def root():
    return {"message": "I am running"}
