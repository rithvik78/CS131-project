# CS131-project

## Requirements
```sh
python3 -m pip install pycryptodome opencv-python pytesseract google-cloud-vision google-cloud-translate google-cloud-texttospeech pillow awscli boto3
```

## Steps to run 

```sh 
cd code
# fill the credentials for aws and gcp
python3 main.py
```

## sample images 

Image: 
![](https://github.com/rithvik78/CS131-project/blob/main/assets/Image.jpeg?raw=true)


Audio: 
[Output](https://github.com/rithvik78/CS131-project/raw/main/assets/test1.mp3)





Image: 
![](https://github.com/rithvik78/CS131-project/blob/main/assets/Image2.png?raw=true)


Audio: 
[Output](https://github.com/rithvik78/CS131-project/raw/main/assets/demo.mp3)


You can watch the [demo video](https://drive.google.com/file/d/1hebbEsJbwptsKQxF7HFrAWXE57-ICUw7/view?usp=sharing)



### On Fog Device

```sh
python3 app.py
```
head to [http://127.0.0.1:5000](http://127.0.0.1:5000) to access the list of translation that you have requested for. 
