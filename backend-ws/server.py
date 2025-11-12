import asyncio
import websockets
import cbor 

active_connections = {}


async def handler(ws):
    async for message in ws:
        incoming_data = cbor.loads(message)
        if incoming_data['request'] == 'handshake':
            user_info = incoming_data.get('data')
            active_connections[user_info['username']] = {'conneciton':ws,'public_key':user_info['public_key'],'stamp':user_info['stamp']}
            print(active_connections)
        if incoming_data['request'] == 'message':
            if incoming_data['data']['to']:
                sent_to = active_connections[incoming_data['data']['to']]
                ws = sent_to['conneciton']
                sent_to_data = incoming_data['data']
                serialized_sent_to = cbor.dumps(sent_to_data)
                await ws.send(serialized_sent_to)

async def main():
    async with websockets.serve(handler, "localhost", 8090):
        print("[+] Server is running at localhost:8090")
        await asyncio.Future()


asyncio.run(main())

