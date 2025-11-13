import secrets
import base64 
def generate_challenge_code():
    return base64.b64encode(secrets.token_bytes(32)).decode()
