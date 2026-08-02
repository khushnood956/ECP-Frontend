import asyncio
import httpx
from uvicorn import Config, Server

async def test_health():
    config = Config(app='main:app', host='127.0.0.1', port=8001, log_level='error')
    server = Server(config=config)
    
    server_task = asyncio.create_task(server.serve())
    await asyncio.sleep(2)
    
    async with httpx.AsyncClient() as client:
        response = await client.get('http://127.0.0.1:8001/health')
        print(f'Status: {response.status_code}')
        print(f'Body: {response.text}')

    server.should_exit = True
    await server_task

asyncio.run(test_health())
