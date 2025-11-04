import asyncio
import websockets
import cbor 

# when a new user connects to the server after a successful handshake it adds their socket object to the active_connections
active_connections = {}


async def handler(ws):
    async for message in ws:
        incoming_data = cbor.loads(message)
        print(incoming_data)
        active_connections[ws] = incoming_data
        



async def main():
    async with websockets.serve(handler, "localhost", 8090):
        print("[+] Server is running at localhost:8070")
        await asyncio.Future()


asyncio.run(main())

