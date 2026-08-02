import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        # Check an endpoint that crashes
        response = await client.get('http://127.0.0.1:8000/crash', headers={'X-Request-ID': 'crash-id'})
        print("Crash Status Code:", response.status_code)
        print("Crash Headers:", response.headers)
        print("Crash JSON:", response.text)

asyncio.run(test_api())
