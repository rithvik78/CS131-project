from flask import Flask, render_template, send_from_directory, request, redirect, url_for, make_response
from Crypto.Cipher import AES
import base64
import boto3
import json
import os
from PIL import Image
import jwt
import datetime

app = Flask(__name__)
app.config['FILES_FOLDER'] = 'files'  # Define the folder to store files

# Load AWS credentials
with open('aws_credentials.json') as json_file:
    credentials = json.load(json_file)

os.environ["AWS_ACCESS_KEY_ID"] = credentials['aws_access_key_id']
os.environ["AWS_SECRET_ACCESS_KEY"] = credentials['aws_secret_access_key']
SECRET_KEY = 'This is a secret' 
KEY = 'This is a key123'.encode()
IV = 'This is an IV456'.encode()
users = {
    "admin": "password",
    "user1": "password1",
    "user2": "password2",
    "user3": "password3",
}
@app.route('/logout')
def logout():
    # Create a response that redirects the user to the home page
    resp = make_response(redirect(url_for('home')))

    # Delete the token
    resp.set_cookie('token', '', expires=0)

    return render_template('login.html')#, error="Invalid username or password")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:  # Validate user credentials
            # User authenticated successfully. Create a token.
            token = jwt.encode({
                'user': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Expiry in 1 day
            }, SECRET_KEY)

            resp = make_response(redirect(url_for('home')))
            resp.set_cookie('token', token)

            return resp

    # Render the login page with an error message if the login attempt failed
    return render_template('login.html', error="Invalid username or password")

def decrypt_image(image_path, key, output_path):
    img = Image.open(image_path)
    data = bytearray(img.tobytes())
    for i, val in enumerate(data):
        data[i] = val ^ key
    img = Image.frombytes(img.mode, img.size, bytes(data))
    img.save(output_path)

def get_s3_client():
    s3 = boto3.client(
        's3',
        region_name='us-west-1',  # Replace 'your-region' with your S3 bucket region
        aws_access_key_id=credentials['aws_access_key_id'],
        aws_secret_access_key=credentials['aws_secret_access_key']
    )
    return s3

def get_table_resource(table_name):
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-2',  # Replace 'your-region' with your DynamoDB table region
        aws_access_key_id=credentials['aws_access_key_id'],
        aws_secret_access_key=credentials['aws_secret_access_key']
    )
    table = dynamodb.Table(table_name)
    return table

def decrypt_text(encrypted_text):
    cipher = AES.new(KEY, AES.MODE_CFB, IV)
    decrypted_text = cipher.decrypt(base64.b64decode(encrypted_text))
    return decrypted_text

@app.route('/')
def home():
    token = request.cookies.get('token')  # Get the JWT from the cookie
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])  # Decode the JWT
    username = payload['user']  # Extract the username from the payload

    # Retrieve the contents from the DynamoDB table
    table_name = 'translationprojectcs131'  # Replace with your table name
    table = get_table_resource(table_name)
    response = table.scan()
    items = response.get('Items', [])

    # Filter the items based on the username and decrypt the description for each item
    items = [item for item in items if item['username'] == username]
    for item in items:
        item['description'] = decrypt_text(item['description']).decode()

    return render_template('index.html', items=items)

# Rest of the code remains the same


@app.route('/audio/<path:filename>')
def audio(filename):
    # Retrieve the audio file from the S3 bucket
    bucket_name = 'translationprojectcs131'  # Replace with your bucket name
    s3_client = get_s3_client()

    # Download the audio file from S3 and save it locally
    local_filename = os.path.join(app.config['FILES_FOLDER'], filename)
    s3_client.download_file(bucket_name, filename, local_filename)

    return send_from_directory(app.config['FILES_FOLDER'], filename)

@app.route('/files/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['FILES_FOLDER'], filename)

@app.route('/images/<path:filename>')
def image(filename):
    # Retrieve the encrypted image file from the S3 bucket
    bucket_name = 'translationprojectcs131'  # Replace with your bucket name
    s3_client = get_s3_client()

    # Download the encrypted image file from S3 and save it locally
    encrypted_image_path = os.path.join(app.config['FILES_FOLDER'], filename)
    s3_client.download_file(bucket_name, filename, encrypted_image_path)

    # Decrypt the image and save it with the same name
    decrypted_image_path = os.path.join(app.config['FILES_FOLDER'], 'decrypted_' + filename)
    decrypt_image(encrypted_image_path, 255, decrypted_image_path)

    # Serve the decrypted image
    return send_from_directory(app.config['FILES_FOLDER'], 'decrypted_' + filename)

if __name__ == '__main__':
    app.run()
