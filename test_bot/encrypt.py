import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from config import *

class AESCipher:
    def __init__(self, key): 
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()  # Key must be 16, 24, or 32 bytes

    def encrypt(self, raw):
        raw = pad(raw.encode('utf-8'), self.bs)  # Pad the input
        cipher = AES.new(self.key, AES.MODE_CBC)  # Use CBC mode
        iv = cipher.iv  # Initialization vector
        enc = cipher.encrypt(raw)
        return base64.b64encode(iv + enc).decode('utf-8')  # Encode and return as string

    def decrypt(self, enc):
        try:
            ct = base64.b64decode(enc.encode("utf-8"))
            iv = ct[:self.bs]
            ct = ct[self.bs:]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), self.bs)
            return pt.decode('utf-8')
        except (ValueError, KeyError):
            return None  # Handle potential errors during decryption


# Example: 
cipher = AESCipher(XXX)

password = "Sh7757723!"
encrypted = cipher.encrypt(password)
print(f"Encrypted password: {encrypted}")

decrypted = cipher.decrypt(encrypted)
print(f"Decrypted password: {decrypted}")