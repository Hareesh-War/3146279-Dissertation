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
Phase 2: Regional Context (Dataset 2 - Bangladesh medicinal plants)
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
│   ├── Completed Notebooks/       # All training notebooks (01-09)
│   │   ├── 01_data_exploration.ipynb
│   │   ├── 02_phase1_baseline.ipynb
│   │   ├── 03_phase2_regional.ipynb
│   │   ├── 04_phase3a_endangered.ipynb
│   │   ├── 05_phase3b_commercial.ipynb
│   │   ├── 06_retrain_improved.ipynb
│   │   ├── 07_dissertation_figures.ipynb
│   │   ├── 08_ablation_study.ipynb
│   │   └── 09_dataset3_test_gradcam.ipynb
│   └── Phase3b Files/             # Saved metrics from Phase 3b
├── webapp/                         # Flask web application
│   ├── app.py
│   ├── database.py
│   ├── templates/
│   ├── static/
│   └── models/
└── data/                           # Datasets (not tracked in git)
```

---

## Datasets

All datasets sourced from Mendeley Data:

| # | Dataset | Species | Images | Role |
|---|---------|---------|--------|------|
| 1 | Indian Medicinal Leaves | 6 | 1,380 | Phase 1 - Baseline |
| 2 | Bangladesh Medicinal Plants | 30 | 1,983 | Phase 2 - Regional |
| 3 | Medicinal Leaf Dataset | 40 | 2,568 | Independent Test Set |
| 4 | Medicinal Plant Dataset | 40 | 3,263 | Phase 3a - Endangered |
| 5 | SIMPD Commercial | 20 | ~360 | Phase 3b - Commercial |

---

## Running the Notebooks

All notebooks run in **Google Colab** with GPU:

1. Upload notebooks from `notebooks/Completed Notebooks/` to Google Drive
2. Open with Google Colab
3. Set runtime to GPU: Runtime -> Change runtime type -> GPU
4. Run cells sequentially

Notebooks should be run in order (01 through 09) as each phase loads the model saved by the previous phase.

---

## Web Application

The Flask web app allows uploading leaf images for species identification.

```bash
cd webapp
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000` in a browser.

---

## Results

Phase 3b validation accuracy: **73.65%** (weighted F1: 73.52%) across 20 species on 463 validation images.

---

## References

1. He, K., et al. (2016). Deep Residual Learning for Image Recognition. CVPR.
2. Yosinski, J., et al. (2014). How transferable are features in deep neural networks? NeurIPS.
3. Selvaraju, R.R., et al. (2017). Grad-CAM: Visual Explanations from Deep Networks. ICCV.

---

**Hareeshwar Muthukumanan** | Student ID: 3146279 | University of Stirling

*Last updated: March 2026*
