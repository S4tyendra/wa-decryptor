from Crypto.Cipher import AES #pip3 install pycryptodome
import zlib #inbuilt


def decrypt_14_db(key_file, db_file, path):
    with open(key_file, "rb") as fh:
        key_data = fh.read()

    key = key_data[126:]
    key_length = len(key)
    print(f"KeyFile Length : {len(key_data)}")
    # print(f"Key Data: {repr(key)} with length of {key_length} bytes")

    with open(db_file, "rb") as fh:
        db_data = fh.read()

    # ---------------signature checks ------------------------------#
    t1 = db_data[15:47]
    t2 = key_data[30:62]
    print(f"DataBase File Signature: {t1}")
    print(f"key File Signature: {t2}")
    if t1==t2:
        print("Database and Key signature Matches")
        for offset in range(185, 196): # Loop through the offset range 185-195
                data = db_data[offset:]
                iv = db_data[67:83]
                length_db_IV = len(iv)
                # print(f"IV DB Data: {repr(iv)} with length of {length_db_IV} bytes")

                try:
                    aes = AES.new(key, mode=AES.MODE_GCM, nonce=iv)
                    with open(path, "wb") as fh:
                        fh.write(zlib.decompress(aes.decrypt(data)))
                        print("[-] " + db_file + " decrypted, '" + path + "' created")
                        break
                except:
                    print(f"Decryption Failed at offset {offset} for KEY FILE {key_file}")
        return([True,"All offsets have been checked."])
    else:
        return([False,"Signature MisMatch"])