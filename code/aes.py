from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

def encrypt(key, iv, plaintext):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()

    padded_plaintext = padder.update(plaintext.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    return ciphertext

def decrypt(key, iv, ciphertext):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

    decrypted_padded_text = decryptor.update(ciphertext) + decryptor.finalize()
    decrypted_text = unpadder.update(decrypted_padded_text) + unpadder.finalize()

    return decrypted_text.decode()


key = b'Sixteen byte key'  # 16-byte key
iv = b'InitializationVe'  # 16-byte IV

plaintext = input('Enter text to encrypt and decrypt: ')

ciphertext = encrypt(key, iv, plaintext)
print("Ciphertext:", ciphertext)

decrypted_text = decrypt(key, iv, ciphertext)
print("Decrypted text:", decrypted_text)
