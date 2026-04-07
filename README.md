# Sequential Transfer Learning for Medicinal Plant Identification

**BSc Software Engineering Dissertation - University of Stirling**

**Author:** Hareeshwar Muthukumanan (3146279)

**Supervisor:** Dr. Shamik Palit

**Module:** CSCU9Z7 - Final Year Dissertation

**Ethics Approval:** GUEP 2025 24485 18893

---

## Overview

This project implements a sequential transfer learning pipeline for identifying medicinal plant species from leaf images using a ResNet50 backbone. The model is trained progressively across multiple datasets, building from general botanical features to specialised species identification.

### Sequential Transfer Learning Pipeline

```
Phase 1: General Features (Dataset 1 - 6 species)
    |
Phase 2: Regional Context (Dataset 2 - 6 Bangladesh species)
    |
Phase 3a: Endangered Species (Dataset 4 - 16 species, high recall)
    |
Phase 3b: Commercial Species (Dataset 5 - 20 species, high precision)
```

---

## Project Structure

```
medicinal-plant-identification/
├── README.md
├── requirements.txt
├── notebooks/
│   ├── Completed Notebooks/
│   │   ├── 01_data_exploration.ipynb
│   │   ├── 02_phase1_baseline.ipynb
│   │   ├── 03_phase2_regional.ipynb
│   │   ├── 04_phase3a_endangered.ipynb
│   │   ├── 05_phase3b_commercial.ipynb
│   │   ├── 06_retrain_improved.ipynb       (EfficientNetB3 training)
│   │   ├── 07_dissertation_figures.ipynb
│   │   ├── 08_ablation_study.ipynb
│   │   ├── 09_dataset3_test_gradcam.ipynb
│   │   ├── 10a_18class_reeval.ipynb        (18-class fair evaluation)
│   │   ├── 10b_multiseed_ablation.ipynb    (5-seed statistical power)
│   │   └── 10c_efficientnet_eval.ipynb     (EfficientNetB3 18-class eval, 99.13%)
│   ├── nb06_improved_files/                (EfficientNetB3 model outputs)
│   └── phase3b_files/                      (Phase 3b model outputs)
├── webapp/
│   ├── app.py
│   ├── database.py
│   ├── requirements.txt
│   ├── templates/
│   ├── static/
│   └── models/
└── data/                                   (Datasets - not tracked)
```

---

## Datasets

All datasets sourced from Mendeley Data:

| # | Dataset | Species | Images | Region | Role |
|---|---------|---------|--------|--------|------|
| 1 | Medicinal Plant Identification | 6 | ~1,380 | Generic | Phase 1 - Baseline |
| 2 | Bangladesh Medicinal Leaves | 6 | ~1,094 | Bangladesh | Phase 2 - Regional |
| 3 | Medicinal Leaf Dataset | 9 | ~900 | Generic | Independent Test Set |
| 4 | REMP - Rare Endangered | 16 | ~3,494 | Bangladesh | Phase 3a - Endangered |
| 5 | SIMPD - South Indian | 20 | ~2,503 | South India | Phase 3b - Commercial |
| **Total** | | **37** (unique) | **~9,551** | | |

---

## Running the Notebooks

All notebooks run in **Google Colab** with GPU:

1. Upload notebooks from `notebooks/Completed Notebooks/` to Google Drive
2. Open with Google Colab
3. Set runtime to GPU: Runtime -> Change runtime type -> GPU
4. Run cells sequentially

Notebooks should be run in order (01 through 09) as each phase loads the model saved by the previous phase. Notebooks 10a, 10b, and 10c are standalone evaluation notebooks.

---

## Web Application

The Flask web app allows uploading leaf images for species identification.

```bash
cd webapp
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000` in a browser.

Features:
- Species identification with confidence scores
- Test-time augmentation (TTA) for robust predictions
- Out-of-distribution detection for unseen species
- Prediction history and species information database

---

## Results

| Model | Accuracy | Notes |
|-------|----------|-------|
| Phase 3b (Sequential, 20 classes) | 70.84% | Cross-regional transfer |
| Phase 3b (Sequential, 18 classes) | 71.43% | Excluding 2 classes with insufficient data |
| Direct Transfer (single seed) | 74.46% | seed=42 |
| Direct Transfer (multi-seed, n=5) | 70.00 ± 2.74% | Seeds: 42, 123, 456, 789, 2024 |
| EfficientNetB3 (18 classes) | 99.13% | Single dataset, class balanced |

Multi-seed replication showed the gap between sequential and direct transfer is not statistically significant (sequential 71.43% falls within the 95% CI [64.63%, 75.37%]).

---

## References

Full references available in the dissertation document (38 sources cited)

---

**Hareeshwar Muthukumaran** | Student ID: 3146279 | University of Stirling

*Last updated: April 2026*
