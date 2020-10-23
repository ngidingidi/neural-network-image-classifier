import pandas as pd
from flask import Flask, render_template, request, redirect
from flask import url_for, send_from_directory
import numpy as np
import os
from werkzeug.utils import secure_filename
import tensorflow as tf
from tensorflow import keras
from PIL import Image, ImageOps

app = Flask(__name__)

app.config['IMAGE_UPLOADS'] = "static/img/uploads"
app.config['ALLOWED_IMAGE_EXTENSIONS'] = ["PNG", "JPG", "JPEG", "GIF"]
app.config['MAX_IMAGE_FILESIZE'] = 2000000 # 2 MB
app.config['TEST_IMAGES'] = "static/my_test/"

def allowed_image(filename):
    
    if not "." in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1]
    if ext.upper() in app.config['ALLOWED_IMAGE_EXTENSIONS']:
        return True
    else:
        return False
    
def allowed_image_filesize(filesize):
    
    if int(filesize) <=app.config['MAX_IMAGE_FILESIZE']:
        return True
    else:
        return False

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    
    if request.method == 'POST':
        
        if request.files:
            
            if not allowed_image_filesize(request.cookies.get('filesize')):
                print('file exceeded maximum size')
                return redirect(request.url)
            
            #print(request.cookies)
            
            image = request.files['image']
            
            if image.filename == '':
                print('image must have a filename')
                return redirect(request.url)
            
            if not allowed_image(image.filename):
                print('That image extension is not allowed')
                return redirect(request.url)
            else:
                global filename
                filename = secure_filename(image.filename)
                
            if filename is not None:
                
                folder = app.config['TEST_IMAGES']
                image = Image.open(folder + filename)
                predictions = import_and_predict(image, model)
                class_names=['buildings', 'forest', 'glacier', 'mountain', 'sea', 'street']
                string="The most likely class of this beautiful image is: " + class_names[np.argmax(predictions)]
                
                imagePath = folder + filename
            
            #image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
            print("Image selected is called: {}".format(filename))
            print(string)
            
            return render_template('upload_image.html', string=string, imagePath=imagePath)
        
    return render_template('upload_image.html')

def load_model():
    model = tf.keras.models.load_model('vgg_classifier_model.h5')
    return model
model = load_model()

def import_and_predict(image_data, model):
    size = (180,180)
    image = ImageOps.fit(image_data, size, Image.ANTIALIAS) 
    img = np.asarray(image)
    img_reshape = img[np.newaxis,...]
    prediction = model.predict(img_reshape)

    return prediction

@app.route("/<path:file_path>")
def send_file(file_path):
    return send_from_directory(app.static_folder, file_path, as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True)