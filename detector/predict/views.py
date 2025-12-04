# predict/views.py
import os
import uuid
import logging
import numpy as np
from pathlib import Path
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from PIL import Image
import joblib
import tensorflow as tf
from .models import Prediction

# Setup logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# PROJECT_ROOT (directory that contains the app folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# MODELS directory: adjust if your models live elsewhere
MODELS_DIR = os.path.join(PROJECT_ROOT, '..', 'models')
CNN_MODEL_PATH = os.path.join(MODELS_DIR, 'cnn_model.h5')
BOOSTER_PATH = os.path.join(MODELS_DIR, 'booster.pkl')

IMG_SIZE = (224, 224)

# Resolve MEDIA_ROOT robustly:
_media_root = getattr(settings, 'MEDIA_ROOT', None)
if not _media_root:
    # fallback to project-level media directory
    _media_root = os.path.join(PROJECT_ROOT, '..', 'media')

# If it's a Path object, convert to str
if isinstance(_media_root, Path):
    MEDIA_ROOT = str(_media_root)
else:
    MEDIA_ROOT = str(_media_root)

# Ensure absolute path
MEDIA_ROOT = os.path.abspath(MEDIA_ROOT)
os.makedirs(MEDIA_ROOT, exist_ok=True)
logger.info("Using MEDIA_ROOT: %s", MEDIA_ROOT)

# optional misclassified folder
MISCLASS_DIR = os.path.join(MEDIA_ROOT, 'misclassified')
os.makedirs(MISCLASS_DIR, exist_ok=True)

# --- Model loading (lazy, robust) ---
cnn = None
feature_model = None
booster = None

def _load_models():
    global cnn, feature_model, booster
    if cnn is None:
        try:
            logger.info("Loading CNN model from %s", CNN_MODEL_PATH)
            cnn = tf.keras.models.load_model(CNN_MODEL_PATH)
            # find GAP layer (fallback)
            gap_layer = None
            for layer in cnn.layers[::-1]:
                if layer.__class__.__name__ == "GlobalAveragePooling2D":
                    gap_layer = layer.name
                    break
            if gap_layer is None:
                gap_layer = cnn.layers[-2].name
            feature_model = tf.keras.Model(inputs=cnn.input, outputs=cnn.get_layer(gap_layer).output)
            logger.info("CNN loaded. Feature extractor ready (GAP: %s).", gap_layer)
        except Exception as e:
            logger.exception("Failed to load CNN model: %s", e)
            # leave cnn as None — prediction attempts will raise clear error

    if booster is None:
        try:
            logger.info("Loading booster model from %s", BOOSTER_PATH)
            booster = joblib.load(BOOSTER_PATH)
            logger.info("Booster loaded.")
        except Exception as e:
            logger.exception("Failed to load booster: %s", e)

# Attempt to load models at import time, but do not crash the server completely
try:
    _load_models()
except Exception:
    logger.warning("Model loading raised an exception at import time (server will still run).")

# Helpers
def preprocess_image_file(path, img_size=IMG_SIZE):
    img = Image.open(path).convert('RGB').resize(img_size)
    arr = np.array(img).astype('float32') / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr, img

def predict_from_array(arr):
    if feature_model is None or booster is None:
        raise RuntimeError("Model(s) not loaded. Check server logs.")
    features = feature_model.predict(arr)
    if features.ndim == 1:
        features = np.expand_dims(features, axis=0)
    if hasattr(booster, "predict_proba"):
        probs = booster.predict_proba(features)[0]
        probability = float(probs[1])
        label = "PNEUMONIA" if probability >= 0.5 else "NORMAL"
    else:
        pred = booster.predict(features)[0]
        label = "PNEUMONIA" if int(pred) == 1 else "NORMAL"
        probability = float(pred if isinstance(pred, (float, int)) else (1.0 if int(pred) == 1 else 0.0))
    return label, probability

# Views
def home(request):
    # render upload page (your template names may vary)
    return render(request, "predict/home.html")

@csrf_exempt
def predict_image(request):
    want_json = False
    if request.GET.get('json') in ('1','true','yes'):
        want_json = True
    accept = request.META.get('HTTP_ACCEPT','')
    if 'application/json' in accept:
        want_json = True

    if request.method != "POST":
        if want_json:
            return JsonResponse({'error': 'POST required'}, status=405)
        return render(request, "predict/home.html")

    if 'image' not in request.FILES:
        if want_json:
            return JsonResponse({'error': 'Missing file field "image"'}, status=400)
        return HttpResponseBadRequest('Missing file field "image"')

    uploaded = request.FILES['image']
    ext = os.path.splitext(uploaded.name)[1] or '.png'
    unique_name = f"{uuid.uuid4().hex}{ext}"

    fs = FileSystemStorage(location=MEDIA_ROOT)
    try:
        saved_name = fs.save(unique_name, uploaded)
        saved_path = fs.path(saved_name)
        logger.debug("Saved uploaded file to %s", saved_path)
    except Exception as e:
        logger.exception("Failed to save uploaded file: %s", e)
        if want_json:
            return JsonResponse({'error': 'Failed to save upload', 'details': str(e)}, status=500)
        return HttpResponseServerError("Failed to save upload")

    try:
        arr, pil_img = preprocess_image_file(saved_path)
    except Exception as e:
        logger.exception("Failed to preprocess image: %s", e)
        if want_json:
            return JsonResponse({'error': 'Failed to open/process image', 'details': str(e)}, status=400)
        return HttpResponseBadRequest("Invalid image file")

    try:
        label, probability = predict_from_array(arr)
    except Exception as e:
        logger.exception("Prediction failed: %s", e)
        if want_json:
            return JsonResponse({'error': 'Prediction failed', 'details': str(e)}, status=500)
        return HttpResponseServerError("Prediction failed")

    # Save to DB best-effort
    try:
        Prediction.objects.create(image=saved_name, label=label, probability=probability)
    except Exception as e:
        logger.warning("DB save failed: %s", e)

    # Save uncertain samples
    try:
        if probability < 0.6:
            suspicious_name = f"{uuid.uuid4().hex}_uncertain{ext}"
            pil_img.save(os.path.join(MISCLASS_DIR, suspicious_name))
            logger.debug("Saved uncertain sample to %s", suspicious_name)
    except Exception:
        logger.exception("Failed to save uncertain image copy")

    if want_json:
        return JsonResponse({
            'prediction': label,
            'probability': probability,
            'image_url': fs.url(saved_name)
        })

    image_url = fs.url(saved_name)
    # compute percent for templates
    probability_percent = round(float(probability) * 100, 2)
    return render(request, "predict/result.html", {
        "prediction": label,
        "probability": probability,
        "probability_percent": probability_percent,
        "image_url": image_url
    })