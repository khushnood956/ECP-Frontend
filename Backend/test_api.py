import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        # Check health endpoint
        response = await client.get('http://127.0.0.1:8000/health', headers={'X-Request-ID': 'my-custom-id'})
        print("Status Code:", response.status_code)
        print("Headers:", response.headers)
        print("JSON:", response.json())

        # Check 404 endpoint (Exception Handler)
        response_404 = await client.get('http://127.0.0.1:8000/not-found', headers={'X-Request-ID': 'my-404-id'})
        print("404 Headers:", response_404.headers)
        print("404 JSON:", response_404.json())

asyncio.run(test_api())
