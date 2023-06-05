from Crypto.Cipher import AES
from datetime import datetime
import uuid
import base64
import os
import cv2
import pytesseract
from google.cloud import vision
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech
from PIL import Image
from aws import (
    upload_file_to_bucket,
    add_metadata_to_dynamodb,
    update_metadata_in_dynamodb,
    get_last_item,
)

KEY = "This is a key123".encode()
IV = "This is an IV456".encode()

key = 255

users = {
    "admin": "password",
    "user1": "password1",
    "user2": "password2",
    "user3": "password3",
}

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_your_service_account_file.json"

# Your bucket and table names
bucket_name = "translationprojectcs131"
table_name = "translationprojectcs131"


def encrypt_text(text):
    cipher = AES.new(KEY, AES.MODE_CFB, IV)
    encrypted_text = base64.b64encode(cipher.encrypt(text.encode()))
    return encrypted_text


def decrypt_text(encrypted_text):
    cipher = AES.new(KEY, AES.MODE_CFB, IV)
    decrypted_text = cipher.decrypt(base64.b64decode(encrypted_text))
    return decrypted_text


def authenticate_user(username, password):
    return username in users and users[username] == password


def process_image_and_text(image_path):
    img = cv2.imread(image_path)
    text_pytesseract = pytesseract.image_to_string(img)
    client = vision.ImageAnnotatorClient()
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    text_vision = (
        response.text_annotations[0].description if response.text_annotations else ""
    )
    text = text_pytesseract if len(text_pytesseract) > len(text_vision) else text_vision
    print(text)
    encrypted_text = encrypt_text(text)
    return encrypted_text


# modify translate_and_speech function to accept output file path as an argument
def translate_and_speech(encrypted_text, audio_file_path):
    decrypted_text = decrypt_text(encrypted_text).decode()
    translate_client = translate.Client()

    # Fetch the list of available languages
    languages = translate_client.get_languages()
    print("Language\tCode")
    for language in languages:
        print(f"{language['name']}\t{language['language']}")

    # Perform translation and text-to-speech with the selected language
    target_language = input("Enter the target language code: ")
    result = translate_client.translate(
        decrypted_text, target_language=target_language, format_="text"
    )
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=result["translatedText"])
    voice = texttospeech.VoiceSelectionParams(
        language_code=target_language, ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=0.9, pitch=0
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(audio_file_path, "wb") as out:
        out.write(response.audio_content)


def encrypt_image(image_path, key, output_path):
    img = Image.open(image_path)
    data = bytearray(img.tobytes())
    for i, val in enumerate(data):
        data[i] = val ^ key
    img = Image.frombytes(img.mode, img.size, bytes(data))
    img.save(output_path)


def encrypt_and_upload_image(image_path, username, encrypted_image_path):
    encrypt_image(image_path, key, encrypted_image_path)
    image_s3_key = upload_file_to_bucket(bucket_name, encrypted_image_path)
    return image_s3_key


# Modify the main function
# def main():
#     username = input('username: ')
#     password = input('password: ')
#     image_input = input('Enter image path or "c" to capture image: ')
#     if image_input.lower() == 'c':
#         cam = cv2.VideoCapture('/dev/video0')  # Open the camera
#         while True:
#             ret, frame = cam.read()  # Read a frame
#             if not ret:
#                 print('Failed to capture image')
#                 break
#             cv2.imshow('Press "c" to capture image, "q" to quit', frame)
#             key = cv2.waitKey(1) & 0xFF
#             # If 'c' is pressed, capture the image
#             if key == ord('c'):
#                 image_path = f"{username}_captured_image.png"
#                 cv2.imwrite(image_path, frame)  # Save the frame to a file
#                 break
#             # If 'q' is pressed, quit without capturing an image
#             elif key == ord('q'):
#                 print('Quitting without capturing image')
#                 return
#         cam.release()  # Close the camera
#         cv2.destroyAllWindows()  # Close the window
#     else:
#         image_path = image_input  # Use the provided image path
#     if os.path.isfile(image_path) and authenticate_user(username, password):
from PIL import Image
import os
import subprocess


def main():
    username = input("username: ")
    password = input("password: ")
    image_input = input('Enter image path or "c" to capture image: ')

    # Capture image if 'c' is selected
    if image_input.lower() == "c":
        cam = cv2.VideoCapture(0)  # Open the camera (0 means default camera)
        while True:
            ret, frame = cam.read()  # Read a frame
            if not ret:
                print("Failed to capture image")
                break
            cv2.imshow('Press "c" to capture image, "q" to quit', frame)
            key = cv2.waitKey(1) & 0xFF

            # If 'c' is pressed, capture the image
            if key == ord("c"):
                image_path = f"{username}_captured_image.png"
                cv2.imwrite(image_path, frame)  # Save the frame to a file
                break
            # If 'q' is pressed, quit without capturing an image
            elif key == ord("q"):
                print("Quitting without capturing image")
                return
        cam.release()  # Close the camera
        cv2.destroyAllWindows()  # Close the window
    else:
        image_path = image_input  # Use the provided image path
    if os.path.isfile(image_path) and authenticate_user(username, password):
        unique_id = str(uuid.uuid4())  # Generate a unique ID
        encrypted_image_path = f"{username}_{unique_id}_encrypted.png"
        audio_file_path = f"{username}_{unique_id}_output.mp3"

        encrypted_text = process_image_and_text(image_path)
        translate_and_speech(encrypted_text, audio_file_path)  # create audio file
        image_s3_key = encrypt_and_upload_image(
            image_path, username, encrypted_image_path
        )
        audio_s3_key = upload_file_to_bucket(bucket_name, audio_file_path)

        sno = str(int(get_last_item(table_name)["sno"]) + 1)
        add_metadata_to_dynamodb(
            table_name, username, encrypted_text.decode(), image_s3_key, audio_s3_key
        )
        update_metadata_in_dynamodb(table_name, sno, username, encrypted_text.decode())
        print("Image/text successfully processed and received by the cloud server.")
    else:
        print("Invalid username or password")


if __name__ == "__main__":
    main()
