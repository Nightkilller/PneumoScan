from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import os, numpy as np, joblib
from PIL import Image
import tensorflow as tf

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, '..', 'models')
CNN_MODEL_PATH = os.path.join(MODELS_DIR, 'cnn_model.h5')
BOOSTER_PATH = os.path.join(MODELS_DIR, 'booster.pkl')
IMG_SIZE = (224,224)

cnn = None
feature_model = None
booster = None

def lazy_load_models():
    global cnn, feature_model, booster
    if cnn is None:
        cnn = tf.keras.models.load_model(CNN_MODEL_PATH)
        gap = None
        for layer in cnn.layers[::-1]:
            if layer.__class__.__name__ == "GlobalAveragePooling2D":
                gap = layer.name
                break
        if gap is None:
            gap = cnn.layers[-2].name
        feature_model = tf.keras.Model(inputs=cnn.input, outputs=cnn.get_layer(gap).output)
    if booster is None:
        booster = joblib.load(BOOSTER_PATH)

def home(request):
    return render(request, "predict/home.html")

@csrf_exempt
def predict_image(request):
    if request.method == "POST":
        lazy_load_models()
        if 'image' not in request.FILES:
            return HttpResponse("No image in request", status=400)
        f = request.FILES['image']
        media_path = os.path.join(PROJECT_ROOT, '..', 'media')
        os.makedirs(media_path, exist_ok=True)
        fs = FileSystemStorage(location=media_path)
        filename = fs.save(f.name, f)
        saved_path = fs.path(filename)

        img = Image.open(saved_path).convert('RGB').resize(IMG_SIZE)
        arr = np.array(img)/255.0
        arr = np.expand_dims(arr, axis=0)
        feats = feature_model.predict(arr)
        pred = booster.predict(feats)[0]
        label = "PNEUMONIA" if int(pred)==1 else "NORMAL"
        return HttpResponse(f"Prediction: {label}")
    return HttpResponse("Send POST with 'image'")
