import asyncio
import base64
import secrets
import websockets
import cbor2 as cbor
from utils import generate_challenge_code
from nacl.signing import VerifyKey

active_connections = {}

async def handler(ws):
    session_token = None
    authenticated_username = None
    
    async for message in ws:
        incoming_data = cbor.loads(message)
        
        if incoming_data['request'] == 'handshake':
            user_info = incoming_data.get('data')
            username = user_info['username']
            
            # Check for duplicate username
            if username in active_connections:
                await ws.send(cbor.dumps({
                    'request': 'auth_failed',
                    'data': {'error': 'Username already taken'}
                }))
                await ws.close()
                return
            
            pubkey = user_info['public_key']
            active_connections[username] = {
                'connection': ws,
                'public_key': pubkey,
                'stamp': user_info['stamp']
            }
            
            challenge_code = generate_challenge_code()
            payload = cbor.dumps({
                'request': 'challenge',
                'data': {'challenge': challenge_code}
            })
            await ws.send(payload)
            
            incoming_response = await ws.recv()
            response = cbor.loads(incoming_response)
            print(f"[*] Challenge response from {username}: {response}")
            
            try:
                VerifyKey(base64.b64decode(pubkey)).verify(
                    response["data"]["challenge"].encode(),
                    base64.b64decode(response['data']['signature']))
                
                # Generate session token
                session_token = secrets.token_urlsafe(32)
                authenticated_username = username
                active_connections[username]['session_token'] = session_token
                
                # Send authentication success with session token
                await ws.send(cbor.dumps({
                    'request': 'auth_success',
                    'data': {'session_token': session_token}
                }))
                print(f"[+] {username} authenticated successfully")
                print(f"[*] Active connections: {list(active_connections.keys())}")
                
            except Exception as e:
                print(f"[-] Authentication failed for {username}: {e}")
                await ws.send(cbor.dumps({
                    'request': 'auth_failed',
                    'data': {'error': 'Invalid signature'}
                }))
                del active_connections[username]
                await ws.close()
                return
        
        elif incoming_data['request'] == 'get_public_key':
            # Verify session token
            provided_token = incoming_data['data'].get('session_token')
            if not session_token or provided_token != session_token:
                await ws.send(cbor.dumps({'error': 'Unauthorized'}))
                continue
            
            requested_username = incoming_data['data']['username']
            if requested_username in active_connections:
                await ws.send(cbor.dumps({
                    'request': 'public_key_response',
                    'data': {
                        'username': requested_username,
                        'public_key': active_connections[requested_username]['public_key']
                    }
                }))
            else:
                await ws.send(cbor.dumps({
                    'request': 'public_key_response',
                    'data': {'error': 'User not found'}
                }))
        
        elif incoming_data['request'] == 'message':
            # Verify session token
            provided_token = incoming_data['data'].get('session_token')
            if not session_token or provided_token != session_token:
                await ws.send(cbor.dumps({'error': 'Unauthorized'}))
                continue
            
            # Verify username matches authenticated user
            if incoming_data['data']['username'] != authenticated_username:
                await ws.send(cbor.dumps({'error': 'Username mismatch'}))
                continue
            
            recipient = incoming_data['data'].get('to')
            if recipient and recipient in active_connections:
                sent_to = active_connections[recipient]
                recipient_ws = sent_to['connection']
                sent_to_data = incoming_data['data']
                serialized_sent_to = cbor.dumps(sent_to_data)
                await recipient_ws.send(serialized_sent_to)
                print(f"[*] Message from {authenticated_username} to {recipient}")
            else:
                await ws.send(cbor.dumps({
                    'error': 'Recipient not found or offline'
                }))
    
    # Cleanup on disconnect
    if authenticated_username and authenticated_username in active_connections:
        del active_connections[authenticated_username]
        print(f"[-] {authenticated_username} disconnected")
        print(f"[*] Active connections: {list(active_connections.keys())}")

async def main():
    async with websockets.serve(handler, "localhost", 8090):
        print("[+] Server is running at localhost:8090")
        await asyncio.Future()

asyncio.run(main())
