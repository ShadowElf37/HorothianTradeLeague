"""
encrypt.py
Project Mercury
Yovel Key-Cohen
"""

def encrypt(msg, key):
    for char in key:
        keys = [chr(ord(char)+i) for i in range(len(msg))]
        msg = ''.join([chr(ord(msg[i])^ord(keys[i])) for i in range(len(msg))])
    return msg

def decrypt(msg, key):
    return encrypt(msg, key)
