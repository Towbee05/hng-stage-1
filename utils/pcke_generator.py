import hashlib
import base64
import secrets

def generate_pcke():
    # Generates a 32-byte secret to authenticate requests
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()
    # Serves as a hasher for code verifier
    code_hasher = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode()

    return code_verifier, code_hasher