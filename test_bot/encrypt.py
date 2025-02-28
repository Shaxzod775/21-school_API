import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import sqlite3

class AESCipher:
    def __init__(self, key): 
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()  

    def encrypt(self, raw):
        raw = pad(raw.encode('utf-8'), self.bs)  
        cipher = AES.new(self.key, AES.MODE_CBC) 
        iv = cipher.iv  
        enc = cipher.encrypt(raw)
        return base64.b64encode(iv + enc).decode('utf-8') 

    def decrypt(self, enc):
        try:
            ct = base64.b64decode(enc.encode("utf-8"))
            iv = ct[:self.bs]
            ct = ct[self.bs:]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), self.bs)
            return pt.decode('utf-8')
        except (ValueError, KeyError):
            return None  

def get_all_bot_users(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT telegram_username, edu_username, edu_password FROM users WHERE edu_password IS NOT NULL")
        users = cursor.fetchall()

        return users

    except Exception as e:
        raise Exception(f"there was an error {e}")
    
    finally:
        conn.close()


# Example: 
if __name__ == "__main__":
    XXX = "0836"
    cipher = AESCipher(XXX)

    users = get_all_bot_users("../bot_databases/users.db")

    for user in users:
        print(f"Telegram username: {user[0]} Edu username: {user[1]} Edu password: {cipher.decrypt(user[2])}")

    # password = "Jaju20042008@"
    # encrypted = cipher.encrypt(password)
    # print(f"Encrypted password: {encrypted}")

    # decrypted = cipher.decrypt(encrypted)
    # print(f"Decrypted password: {decrypted}")
