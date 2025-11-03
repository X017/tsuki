import asyncio
import websockets
import json



# when a new user connects to the server after a successful handshake it adds their socket object to the active_connections 
active_connections = {} 


async def handler(ws):
    async for message in ws:
        input_data = json.loads(message)
        username = input_data['username']
        to = active_connections.get(input_data['to'])
        if to:
            await to.send(input_data['message'])
        active_connections[username] = ws

async def main():
    async with websockets.serve(handler,"localhost",8090):
        print("[+] Server is running at localhost:8070")
        await asyncio.Future()

asyncio.run(main())


