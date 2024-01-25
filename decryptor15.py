# 15
import hmac
from hashlib import sha256
import javaobj
from Crypto.Cipher import AES
import zlib


def _generate_hmac_of_hmac(key_stream):
    key = hmac.new(
        hmac.new(b'\x00' * 32, key_stream, sha256).digest(),
        b"backup encryption\x01",
        sha256
    )
    return key.digest(), key_stream


def _extract_encrypted_key(keyfile):
    key_stream = b""
    for byte in javaobj.loads(keyfile):
        key_stream += byte.to_bytes(1, "big", signed=True)
    return _generate_hmac_of_hmac(key_stream)


def decrypt_15_db(key_file, db_file, path):
    # Read encrypted data
    with open(db_file, "rb") as fh:
        encrypted = fh.read()

    with open(key_file, "rb") as fh:
        key_data = fh.read()

    # Extract encrypted key and generate HMAC-based key
    hmac_key, key_stream = _extract_encrypted_key(key_data)
    print("HMAC-based key:", hmac_key)
    print("Key stream:", key_stream)

    main_key = hmac_key
    iv = encrypted[8:24]
    db_offset = encrypted[0] + 2
    db_ciphertext = encrypted[db_offset:]

    # Decrypt and decompress data
    cipher = AES.new(main_key, AES.MODE_GCM, iv)
    db_compressed = cipher.decrypt(db_ciphertext)
    db = zlib.decompress(db_compressed)

    # Save decrypted data to file
    with open(path, 'wb') as file:
        file.write(db)
