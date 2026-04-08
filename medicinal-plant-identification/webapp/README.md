# Web Application - Medicinal Plant Identification

## Quick Start

### 1. Install Dependencies
```bash
cd webapp
pip install -r requirements.txt
```

### 2. Add Your Trained Model
Copy your trained model files from Google Drive to `webapp/models/`:
- `phase3b_commercial.h5` (or `.keras`)
- `phase3b_class_names.json`

**In Google Colab, download like this:**
```python
from google.colab import files
files.download('/content/drive/MyDrive/MedicinalPlant_Dissertation/models/phase3b_commercial.h5')
files.download('/content/drive/MyDrive/MedicinalPlant_Dissertation/models/phase3b_class_names.json')
```

### 3. Run the App
```bash
python app.py
```

### 4. Open in Browser
Go to: **http://localhost:5000**

---

## Features

| Page | URL | Description |
|------|-----|-------------|
| Identify | `/` | Upload/capture plant image for identification |
| Species | `/species` | Browse all species with search & filters |
| History | `/history` | View past predictions |
| About | `/about` | Project information |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Upload image, get prediction |
| GET | `/api/species/<name>` | Get species info (JSON) |
| GET | `/api/stats` | System statistics (JSON) |

## Architecture

```
Browser (HTML5/JS/CSS)
    |
    |-- Camera Capture (HTML5 MediaDevices API)
    |-- Image Upload (drag & drop / file select)
    |
Flask Backend (Python)
    |
    |-- /predict --> TensorFlow Model --> Results
    |-- /species --> SQLite Database --> Species Info
    |-- /history --> SQLite Database --> Prediction Logs
    |
SQLite Database
    |-- species table (name, conservation_status, harvesting_legal, ...)
    |-- predictions table (timestamp, image, species, confidence, ...)
```

## File Structure
```
webapp/
    app.py              # Flask application (main entry point)
    database.py         # SQLite database manager
    requirements.txt    # Python dependencies
    README.md           # This file
    models/             # Place .h5 model files here
    static/
        css/style.css   # Responsive stylesheet
        js/app.js       # Frontend JavaScript
        uploads/        # Uploaded images (auto-created)
    templates/
        base.html       # Base template
        index.html      # Home / identify page
        species.html    # Species database
        species_detail.html
        history.html    # Prediction history
        about.html      # Project information
```
