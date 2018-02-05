def encrypt(msg, key):
	"""
	Powerful XOR encryption tool.
	The encryption key is taken one character at a time.
	A new list of keys is created, each adding 2*i to the one character.
	It encrypts the message character by character for those sequential keys.
	This is repeated for every character in the key, encrypting multiple times to the point of unrecognizablility.
	"""
    for char in key:
        keys = [chr(ord(char)+i*2) for i in range(len(msg))]
        msg = ''.join([chr(ord(msg[i])^ord(keys[i])) for i in range(len(msg))])
    return msg

def decrypt(msg, key):
    return encrypt(msg, key)
