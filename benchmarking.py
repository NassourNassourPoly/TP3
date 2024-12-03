import asyncio
import time
import os
import aiohttp

# Function to call the endpoint
async def call_endpoint_http(session, request_num, endpoint, method="get"):
    url = f"http://{os.getenv("GATEKEEPER_IP")}:8000{endpoint}"  # Replace with your actual URL
    headers = {'Content-Type': 'application/json'}
    try:
        if(method == "post"):
            async with session.post(url, headers=headers) as response:
                status_code = response.status
                response_json = await response.json()
                print(f"Request {request_num}: Status Code: {status_code}")
                return status_code, response_json
        else:
            async with session.get(url, headers=headers) as response:
                status_code = response.status
                response_json = await response.json()
                print(f"Request {request_num}: Status Code: {status_code}")
                return status_code, response_json
    except Exception as e:
        print(f"Request {request_num}: Failed - {str(e)}")
        return None, str(e)

# Main function to handle the requests
async def main():
    num_requests = 1000  # Number of requests to send
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [call_endpoint_http(session, i, "/read/direct") for i in range(num_requests)]
        await asyncio.gather(*tasks)
    end_time = time.time()
    time_read_direct = end_time - start_time

    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [call_endpoint_http(session, i, "/read/random") for i in range(num_requests)]
        await asyncio.gather(*tasks)
    end_time = time.time()
    time_read_random = end_time - start_time

    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [call_endpoint_http(session, i, "/read/customized") for i in range(num_requests)]
        await asyncio.gather(*tasks)
    end_time = time.time()
    time_read_customized = end_time - start_time

    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [call_endpoint_http(session, i, "/write", "post") for i in range(num_requests)]
        await asyncio.gather(*tasks)
    end_time = time.time()
    time_write = end_time - start_time

    print("\nRead Direct: ")
    print(f"Total time taken: {time_read_direct:.2f} seconds")
    print(f"Average time per request: {(time_read_direct) / num_requests:.4f} seconds")

    print("\nRead Random: ")
    print(f"Total time taken: {time_read_random:.2f} seconds")
    print(f"Average time per request: {(time_read_random) / num_requests:.4f} seconds")

    print("\nRead Customized: ")
    print(f"Total time taken: {time_read_customized:.2f} seconds")
    print(f"Average time per request: {(time_read_customized) / num_requests:.4f} seconds")

    print("\nWrite: ")
    print(f"Total time taken: {time_write:.2f} seconds")
    print(f"Average time per request: {(time_write) / num_requests:.4f} seconds")
    print()
# Entry point for the script
if __name__ == "__main__":
    asyncio.run(main())


