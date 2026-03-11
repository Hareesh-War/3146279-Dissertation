"""
Flask Web Application - Medicinal Plant Identification
======================================================
Sequential Transfer Learning for Medicinal Plant Identification:
Endangered Species Protection and Sustainable Harvesting

Student: Hari (3146279) | BSc Software Engineering | University of Stirling
Supervisor: Dr. Shamik Palit

This Flask application serves the trained deep learning model as a REST API
with a mobile-responsive web interface for plant identification.

Architecture:
    Browser (HTML5/JS) -> Flask API -> TensorFlow Model -> SQLite DB
                       -> Camera Capture -> /predict endpoint
                       -> Species Info -> /species endpoint
                       -> History Log  -> /history endpoint
"""

import os
import json
import uuid
import sqlite3
from datetime import datetime

import numpy as np
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image

# TensorFlow import with GPU memory management
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF warnings
import tensorflow as tf

from database import DatabaseManager

# ============================================================
# Configuration
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}
IMG_SIZE = (224, 224)  # Will be updated when model loads
MODEL_TYPE = 'resnet50'  # Will be updated when model loads ('resnet50' or 'efficientnet')
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence to show prediction

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# ============================================================
# Flask App
# ============================================================
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['SECRET_KEY'] = 'medicinal-plant-id-3146279'

# ============================================================
# Global State
# ============================================================
model = None
class_names = []
db = DatabaseManager(os.path.join(BASE_DIR, 'plant_identification.db'))

# Number of TTA augmentations to average (1 = no TTA, 5 = recommended)
TTA_AUGMENTATIONS = 5


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _rebuild_model_from_keras_zip(keras_path):
    """
    Rebuild model architecture and load weights from a .keras ZIP file.
    
    This bypasses TF version incompatibilities (e.g. TF 2.19 -> 2.20)
    where load_model() fails due to BatchNormalization deserialization bugs.
    
    Steps:
        1. Read config.json from the .keras ZIP to get layer structure
        2. Rebuild the exact architecture in code
        3. Extract model.weights.h5 and load weights
    """
    import zipfile
    import tempfile
    import shutil
    
    from tensorflow.keras import layers
    
    # Read architecture config
    with zipfile.ZipFile(keras_path, 'r') as z:
        config = json.loads(z.read('config.json'))
    
    layer_configs = config['config']['layers']
    
    # Detect architecture from config
    layer_sequence = []
    for lc in layer_configs:
        cls = lc['class_name']
        name = lc['config'].get('name', '')
        if cls == 'InputLayer':
            continue
        elif cls == 'Sequential' and 'augmentation' in name:
            # Data augmentation sub-model
            aug_layers = []
            for al in lc['config'].get('layers', []):
                acls = al['class_name']
                if acls == 'InputLayer':
                    continue
                elif acls == 'RandomFlip':
                    aug_layers.append(layers.RandomFlip(al['config'].get('mode', 'horizontal')))
                elif acls == 'RandomRotation':
                    factor = al['config'].get('factor', [-0.1, 0.1])
                    aug_layers.append(layers.RandomRotation(factor))
                elif acls == 'RandomZoom':
                    aug_layers.append(layers.RandomZoom(al['config'].get('height_factor', 0.1)))
                elif acls == 'RandomContrast':
                    factor = al['config'].get('factor', [0, 0.1])
                    aug_layers.append(layers.RandomContrast(factor))
            layer_sequence.append(('augmentation', tf.keras.Sequential(aug_layers, name=name)))
        elif cls == 'Functional' and 'resnet50' in name.lower():
            base = tf.keras.applications.ResNet50(
                weights="imagenet", include_top=False, input_shape=(224, 224, 3)
            )
            base.trainable = lc['config'].get('trainable', True)
            layer_sequence.append(('resnet50', base))
        elif cls == 'GlobalAveragePooling2D':
            layer_sequence.append(('gap', layers.GlobalAveragePooling2D()))
        elif cls == 'BatchNormalization':
            layer_sequence.append(('bn', layers.BatchNormalization()))
        elif cls == 'Dropout':
            rate = lc['config'].get('rate', 0.5)
            layer_sequence.append(('dropout', layers.Dropout(rate)))
        elif cls == 'Dense':
            units = lc['config']['units']
            activation = lc['config'].get('activation', 'linear')
            layer_sequence.append(('dense', layers.Dense(units, activation=activation)))
    
    # Build Sequential model
    model_layers = [tf.keras.Input(shape=(224, 224, 3))]
    for _, layer in layer_sequence:
        model_layers.append(layer)
    
    model_name = config['config'].get('name', 'rebuilt_model')
    rebuilt = tf.keras.Sequential(model_layers, name=model_name)
    
    # Extract and load weights
    temp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(keras_path, 'r') as z:
            z.extract('model.weights.h5', temp_dir)
        weights_path = os.path.join(temp_dir, 'model.weights.h5')
        rebuilt.load_weights(weights_path)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return rebuilt


def load_model():
    """Load the trained TensorFlow model and class names."""
    global model, class_names

    # Try loading in priority order: improved > phase3b > phase3a > phase2 > phase1
    model_files = [
        ('improved_model.keras', 'improved_class_names.json'),
        ('improved_model.h5', 'improved_class_names.json'),
        ('phase3b_commercial.keras', 'phase3b_class_names.json'),
        ('phase3b_commercial.h5', 'phase3b_class_names.json'),
        ('phase3a_endangered.keras', 'phase3a_class_names.json'),
        ('phase3a_endangered.h5', 'phase3a_class_names.json'),
        ('phase2_regional.keras', 'phase2_class_names.json'),
        ('phase2_regional.h5', 'phase2_class_names.json'),
        ('phase1_baseline.keras', 'phase1_class_names.json'),
        ('phase1_baseline.h5', 'phase1_class_names.json'),
    ]

    for model_file, class_file in model_files:
        model_path = os.path.join(MODEL_DIR, model_file)
        class_path = os.path.join(MODEL_DIR, class_file)

        if os.path.exists(model_path):
            print(f"Loading model: {model_file}")
            try:
                loaded = False
                load_errors = []

                # Strategy 1: Direct load (works when TF versions match)
                try:
                    model = tf.keras.models.load_model(model_path, compile=False)
                    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
                    loaded = True
                except Exception as e1:
                    load_errors.append(f"  Strategy 1 (direct load): {e1}")

                # Strategy 2: Rebuild architecture + load weights from .keras ZIP
                # Bypasses TF version incompatibilities (e.g. 2.19 -> 2.20)
                if not loaded and model_file.endswith('.keras'):
                    try:
                        print("  Trying architecture rebuild + weight loading...")
                        model = _rebuild_model_from_keras_zip(model_path)
                        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
                        loaded = True
                        print("  Loaded via architecture rebuild!")
                    except Exception as e2:
                        load_errors.append(f"  Strategy 2 (rebuild+weights): {e2}")

                if not loaded:
                    for err in load_errors:
                        print(err)
                    raise RuntimeError("All loading strategies failed")

                print(f"  Model loaded successfully!")
                try:
                    print(f"  Input shape: {model.input_shape}")
                    print(f"  Output classes: {model.output_shape[-1]}")
                except Exception:
                    print(f"  (Could not print model shape info)")

                # Load class names
                if os.path.exists(class_path):
                    with open(class_path, 'r') as f:
                        class_names = json.load(f)
                    print(f"  Class names: {class_names}")
                else:
                    num_classes = model.output_shape[-1]
                    class_names = [f"Species_{i}" for i in range(num_classes)]
                    print(f"  Warning: No class names file. Using generic names.")

                # Detect model type from input shape
                try:
                    input_shape = model.input_shape
                    if input_shape[1] == 300:  # EfficientNetB3
                        IMG_SIZE = (300, 300)
                        MODEL_TYPE = 'efficientnet'
                        print(f"  Detected EfficientNet model (300x300)")
                    else:
                        IMG_SIZE = (224, 224)
                        MODEL_TYPE = 'resnet50'
                        print(f"  Detected ResNet50 model (224x224)")
                except:
                    pass

                return True
            except Exception as e:
                print(f"  Error loading {model_file}: {e}")
                continue

    print("\n" + "=" * 50)
    print("WARNING: No model files found!")
    print(f"Place your .h5 or .keras model files in: {MODEL_DIR}")
    print("The app will run in demo mode without predictions.")
    print("=" * 50 + "\n")
    return False


def check_vegetation(image_path, threshold=0.10):
    """
    Check if an image contains significant green vegetation.
    Uses HSV color space to detect green-ish pixels.
    Returns (is_plant_image: bool, vegetation_ratio: float)
    """
    img = Image.open(image_path).convert('RGB')
    img_small = img.resize((128, 128))  # Downscale for speed
    pixels = np.array(img_small, dtype=np.float32)

    # Convert RGB to HSV manually
    r, g, b = pixels[:,:,0]/255, pixels[:,:,1]/255, pixels[:,:,2]/255
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    diff = cmax - cmin

    # Hue calculation (0-360)
    hue = np.zeros_like(cmax)
    mask_r = (cmax == r) & (diff > 0)
    mask_g = (cmax == g) & (diff > 0)
    mask_b = (cmax == b) & (diff > 0)
    hue[mask_r] = (60 * ((g[mask_r] - b[mask_r]) / diff[mask_r]) + 360) % 360
    hue[mask_g] = (60 * ((b[mask_g] - r[mask_g]) / diff[mask_g]) + 120) % 360
    hue[mask_b] = (60 * ((r[mask_b] - g[mask_b]) / diff[mask_b]) + 240) % 360

    saturation = np.where(cmax > 0, diff / cmax, 0)
    value = cmax

    # Green vegetation: hue 35-160, saturation > 0.15, value > 0.10
    green_mask = (hue >= 35) & (hue <= 160) & (saturation > 0.15) & (value > 0.10)
    vegetation_ratio = float(np.mean(green_mask))

    return vegetation_ratio >= threshold, vegetation_ratio


def calculate_entropy(probabilities):
    """
    Calculate Shannon entropy of prediction distribution.
    Higher entropy = model is more uncertain / spread across classes.
    """
    probs = np.array(probabilities)
    probs = probs[probs > 1e-10]  # Filter near-zero to avoid log(0)
    entropy = -np.sum(probs * np.log2(probs))
    # Max possible entropy for N classes
    max_entropy = np.log2(len(probabilities))
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    return float(entropy), float(normalized_entropy)


def preprocess_image(image_path):
    """Preprocess an image for model prediction.
    
    Auto-detects preprocessing based on model type:
    - EfficientNet: uses tf.keras.applications.efficientnet.preprocess_input (scales to [-1,1])
    - ResNet50: uses /255 normalization (scales to [0,1]) matching training pipeline
    """
    img = Image.open(image_path).convert('RGB')
    img = img.resize(IMG_SIZE, Image.LANCZOS)
    img_array = np.array(img, dtype=np.float32)
    
    if MODEL_TYPE == 'efficientnet':
        # EfficientNet preprocessing: scales to [-1, 1]
        img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
    else:
        # ResNet50: normalize to [0, 1] matching training pipeline
        img_array /= 255.0
    
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array


def preprocess_image_tta(image_path):
    """Create multiple augmented versions for Test-Time Augmentation.
    
    Returns a batch of augmented images. Predictions are averaged
    for more robust results, reducing sensitivity to orientation/lighting.
    """
    img = Image.open(image_path).convert('RGB')
    img = img.resize(IMG_SIZE, Image.LANCZOS)
    base = np.array(img, dtype=np.float32)
    
    augmented = [base]  # Original
    
    # Horizontal flip
    augmented.append(np.fliplr(base))
    
    # Slight rotations using numpy
    # 90-degree rotation
    augmented.append(np.rot90(base, k=1)[:IMG_SIZE[0], :IMG_SIZE[1], :]  
                     if base.shape[0] == base.shape[1] else base)
    
    # Brightness variations
    augmented.append(np.clip(base * 1.1, 0, 255))  # Brighter
    augmented.append(np.clip(base * 0.9, 0, 255))  # Darker
    
    # Preprocess all
    batch = np.stack(augmented[:TTA_AUGMENTATIONS])
    
    if MODEL_TYPE == 'efficientnet':
        batch = tf.keras.applications.efficientnet.preprocess_input(batch)
    else:
        batch = batch / 255.0
    
    return batch


def predict_plant(image_path):
    """Run prediction on an image and return results with OOD detection."""
    if model is None:
        return {
            'success': False,
            'error': 'No model loaded. Please place model files in webapp/models/',
            'predictions': []
        }

    try:
        # --- OOD Check 1: Vegetation color analysis ---
        is_plant_image, vegetation_ratio = check_vegetation(image_path)

        # --- Run model prediction (with TTA if available) ---
        if TTA_AUGMENTATIONS > 1:
            img_batch = preprocess_image_tta(image_path)
            all_preds = model.predict(img_batch, verbose=0)
            predictions = np.mean(all_preds, axis=0)  # Average predictions
        else:
            img_array = preprocess_image(image_path)
            predictions = model.predict(img_array, verbose=0)[0]

        # --- OOD Check 2: Prediction entropy ---
        entropy, normalized_entropy = calculate_entropy(predictions)
        # Uncertain if normalized entropy > 0.45 (fairly spread across classes)
        is_uncertain = normalized_entropy > 0.45

        # Get top 5 predictions
        top_indices = np.argsort(predictions)[::-1][:5]
        results = []
        for idx in top_indices:
            confidence = float(predictions[idx])
            species_name = class_names[idx] if idx < len(class_names) else f"Species_{idx}"
            species_info = db.get_species(species_name)

            result = {
                'species': species_name,
                'confidence': round(confidence * 100, 1),
                'conservation_status': species_info.get('conservation_status', 'Unknown') if species_info else 'Unknown',
                'harvesting_legal': species_info.get('harvesting_legal', None) if species_info else None,
                'description': species_info.get('description', '') if species_info else ''
            }
            results.append(result)

        top_prediction = results[0]

        # --- Build warning message ---
        warning = None
        if not is_plant_image:
            warning = ('This image may not contain a plant. '
                       'The model can only identify medicinal plants — '
                       f'only {round(vegetation_ratio * 100, 1)}% of the image appears to be vegetation. '
                       'Confidence scores may be unreliable.')
        elif is_uncertain:
            warning = ('The model is uncertain between multiple species. '
                       'Consider taking a clearer photo of the leaf against a plain background.')

        return {
            'success': True,
            'predictions': results,
            'top_species': top_prediction['species'],
            'top_confidence': top_prediction['confidence'],
            'is_confident': top_prediction['confidence'] >= CONFIDENCE_THRESHOLD * 100,
            'is_plant_image': is_plant_image,
            'vegetation_ratio': round(vegetation_ratio * 100, 1),
            'prediction_entropy': round(entropy, 3),
            'normalized_entropy': round(normalized_entropy, 3),
            'is_uncertain': is_uncertain,
            'warning': warning
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'predictions': []
        }


# ============================================================
# Routes
# ============================================================

@app.route('/')
def index():
    """Main page with camera capture and upload."""
    model_loaded = model is not None
    recent = db.get_recent_predictions(limit=5)
    return render_template('index.html',
                           model_loaded=model_loaded,
                           recent_predictions=recent)


@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint: Accept image, run model, return results."""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Use JPG, PNG, or BMP.'}), 400

    # Save uploaded image
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)

    # Run prediction
    result = predict_plant(filepath)

    # Log to database
    if result['success']:
        db.log_prediction(
            image_path=f'uploads/{filename}',
            predicted_species=result['top_species'],
            confidence=result['top_confidence'],
            all_predictions=json.dumps(result['predictions'])
        )

    # Add image URL to result
    result['image_url'] = f'/static/uploads/{filename}'
    return jsonify(result)


@app.route('/species')
def species_list():
    """List all known species with info."""
    all_species = db.get_all_species()
    return render_template('species.html', species=all_species)


@app.route('/species/<name>')
def species_detail(name):
    """Detailed info about a specific species."""
    species = db.get_species(name)
    if species is None:
        return render_template('species_detail.html', species=None, name=name)
    return render_template('species_detail.html', species=species, name=name)


@app.route('/history')
def history():
    """View prediction history."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    predictions = db.get_recent_predictions(limit=per_page, offset=(page - 1) * per_page)
    total = db.get_prediction_count()
    return render_template('history.html',
                           predictions=predictions,
                           page=page,
                           total=total,
                           per_page=per_page)


@app.route('/about')
def about():
    """About page with project info."""
    return render_template('about.html')


@app.route('/api/species/<name>')
def api_species(name):
    """REST API: Get species info as JSON."""
    species = db.get_species(name)
    if species:
        return jsonify(species)
    return jsonify({'error': 'Species not found'}), 404


@app.route('/api/stats')
def api_stats():
    """REST API: Get system statistics."""
    stats = {
        'model_loaded': model is not None,
        'total_species': len(class_names),
        'total_predictions': db.get_prediction_count(),
        'class_names': class_names
    }
    return jsonify(stats)


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("MEDICINAL PLANT IDENTIFICATION SYSTEM")
    print("Sequential Transfer Learning | BSc Dissertation")
    print("Student: Hari (3146279) | University of Stirling")
    print("=" * 60)

    # Initialize database
    db.initialize()
    print("\nDatabase initialized")

    # Load model
    model_loaded = load_model()
    if model_loaded:
        print(f"\nModel ready with {len(class_names)} species")
    else:
        print("\nRunning in demo mode (no model)")

    print(f"\nStarting web server...")
    print(f"Open: http://localhost:5000")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
