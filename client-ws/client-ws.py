import asyncio
import websockets
import json
import cbor 
from nacl.public import Box, PrivateKey

user_secret_key = PrivateKey.generate()
user_public_key = user_secret_key.public_key


async def send_messages(ws, username):
    """Read messages from stdin and send them to the server."""
    while True:
        print("Enter message in format: <recipient> <text>")
        try:
            user_input = await asyncio.get_event_loop().run_in_executor(None, input)
            if not user_input.strip():
                continue
            parts = user_input.split(" ", 1)
            if len(parts) < 2:
                print("Invalid format. Use: <recipient> <message>")
                continue
            recipient, message_text = parts
            payload = {
                "username": username,
                "to": recipient,
                "message": message_text
            }
            await ws.send(json.dumps(payload))
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error sending message: {e}")


async def receive_messages(ws):
    """Listen for incoming messages from the server."""
    try:
        async for message in ws:
            print(f"\n[INCOMING] {message}")
    except websockets.exceptions.ConnectionClosed:
        print("\n[INFO] Connection closed.")


async def main():
    uri = "ws://localhost:8090"
    username = input("Enter your username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return
    connection_credentials = {
        "request":1,
        "username":username,
        "public_key":bytes(user_public_key)
    }


    try:
        async with websockets.connect(uri) as ws:
            print(f"[+] Connected to server as '{username}'")
            print(f"[=] connection_credentials {connection_credentials}")
            await ws.send(cbor.dumps(connection_credentials))
            # Start receiving and sending concurrently
            receiver = asyncio.create_task(receive_messages(ws))
            sender = asyncio.create_task(send_messages(ws, username))

            # Wait until either task completes (e.g., user quits or connection drops)
            done, pending = await asyncio.wait(
                [receiver, sender],
                return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())

