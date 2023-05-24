from PIL import Image

def encrypt_image(image_path, key):
    with Image.open(image_path) as img:
        img_data = bytearray(img.tobytes())
        encrypted_data = bytearray()

        for byte in img_data:
            encrypted_byte = byte ^ key 
            encrypted_data.append(encrypted_byte)

        encrypted_image = Image.frombytes(img.mode, img.size, bytes(encrypted_data))
        encrypted_image.save("encrypted_image.png")

def decrypt_image(encrypted_image_path, key):
    with Image.open(encrypted_image_path) as encrypted_img:
        encrypted_data = bytearray(encrypted_img.tobytes())
        decrypted_data = bytearray()

        for byte in encrypted_data:
            decrypted_byte = byte ^ key 
            decrypted_data.append(decrypted_byte)

        decrypted_image = Image.frombytes(encrypted_img.mode, encrypted_img.size, bytes(decrypted_data))
        decrypted_image.save("decrypted.png")


image_path = input('Specify the path of the image: ') 
key = 255

encrypt_image(image_path, key)
print("Image encrypted successfully.")

encrypted_image_path = "encrypted_image.png"

decrypt_image(encrypted_image_path, key)
print("Image decrypted successfully.")
