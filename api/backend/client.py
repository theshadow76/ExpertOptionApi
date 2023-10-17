import asyncio
import websockets

async def MainClient(server, data):
    async with websockets.connect(server) as websocket:
        await websocket.send(data)
        response = await websocket.recv()
        return response


