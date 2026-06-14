import base64
import binascii

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

class EventWebhook:
    def __init__(self) -> None:
        _raw_public_key = "MCowBQYDK2VwAyEAjSICb9pp0kHizGQtdG8ySWsDChfGqi+gyFCttigBNOA="
        _public_key_bytes = base64.b64decode(_raw_public_key)
        self.public_key = serialization.load_der_public_key(_public_key_bytes)
    
    def _verify_signature(self, raw_body: bytes, sighex: str, timestamp: str) -> bool:
        if not isinstance(self.public_key, Ed25519PublicKey):
            return False
        
        message = timestamp.encode() + raw_body
        sighex_bytes = binascii.unhexlify(sighex)
        
        try:
            self.public_key.verify(sighex_bytes, message)
            return True
        except InvalidSignature:
            return False