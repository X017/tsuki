import asyncio
import base64
import secrets
import websockets
import cbor2 as cbor
from nacl.signing import SigningKey
from nacl.public import PrivateKey

user_secret_key = PrivateKey.generate()
user_public_key = user_secret_key.public_key
session_token = None

def client_handshake_payload(username, public_key):
    payload = {
        "request": "handshake",
        "data": {
            "username": username,
            "public_key": public_key,
            "stamp": secrets.token_hex(16)
        }
    }
    return cbor.dumps(payload)

def generate_signing_keypair():
    key = SigningKey.generate()
    pub = base64.b64encode(key.verify_key.encode()).decode()
    return key, pub

async def send_messages(ws, username):
    global session_token
    while True:
        user_input = await asyncio.get_event_loop().run_in_executor(None, input)
        if not user_input.strip():
            continue
        
        try:
            recipient, message_text = user_input.split(" ", 1)
        except ValueError:
            print("[!] Format: <recipient> <message>")
            continue
        
        payload = {
            "request": "message",
            "data": {
                "username": username,
                "to": recipient,
                "message": message_text,
                "session_token": session_token
            }
        }
        await ws.send(cbor.dumps(payload))

async def receive_messages(ws):
    async for message in ws:
        incoming_data = cbor.loads(message)
        
        if 'error' in incoming_data:
            print(f"[!] Error: {incoming_data['error']}")
        elif 'username' in incoming_data and 'message' in incoming_data:
            print(f"\n{incoming_data['username']}: {incoming_data['message']}")
        else:
            print(f"[*] Server response: {incoming_data}")

async def main():
    global session_token
    uri = "ws://localhost:8090"
    username = input("Enter your username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return
    
    sign_key, pub_key = generate_signing_keypair()
    handshake_payload = client_handshake_payload(username, pub_key)
    
    async with websockets.connect(uri) as ws:
        await ws.send(handshake_payload)
        print("[*] Handshake sent.")
        
        incoming_challenge = await ws.recv()
        challenge_data = cbor.loads(incoming_challenge)
        
        if challenge_data['request'] == 'auth_failed':
            print(f"[-] Authentication failed: {challenge_data['data']['error']}")
            return
        
        challenge = challenge_data["data"]['challenge']
        signature = sign_key.sign(challenge.encode()).signature
        
        response = {
            "request": "challenge",
            "data": {
                "username": username,
                "challenge": challenge,
                "signature": base64.b64encode(signature).decode()
            }
        }
        await ws.send(cbor.dumps(response))
        print("[*] Challenge response sent.")
        
        # Wait for authentication result
        auth_result = await ws.recv()
        auth_data = cbor.loads(auth_result)
        
        if auth_data['request'] == 'auth_success':
            session_token = auth_data['data']['session_token']
            print("[+] Authentication successful!")
            print("[*] You can now send messages. Format: <recipient> <message>")
        else:
            print(f"[-] Authentication failed: {auth_data['data'].get('error', 'Unknown error')}")
            return
        
        receiver = asyncio.create_task(receive_messages(ws))
        sender = asyncio.create_task(send_messages(ws, username))
        await asyncio.wait([receiver, sender], return_when=asyncio.FIRST_COMPLETED)

if __name__ == "__main__":
    asyncio.run(main())
