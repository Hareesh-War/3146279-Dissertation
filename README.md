# Sequential Transfer Learning for Medicinal Plant Identification

**BSc Software Engineering Dissertation - University of Stirling**

**Author:** Hareeshwar Muthukumanan (3146279)

**Supervisor:** Dr. Shamik Palit

**Module:** CSCU9Z7 - Final Year Dissertation

**Ethics Approval:** GUEP 2025 24485 18893

---
## Key Links
* GitHub Repository: https://github.com/Hareesh-War/3146279-Dissertation
* Google Drive (training data & models): https://drive.google.com/drive/folders/1RQGF7XmuYf-3XZJV5sNhjfle0h0Ge6FC?usp=sharing
* Onedrive: https://stir-my.sharepoint.com/:f:/g/personal/ham00411_students_stir_ac_uk/IgDIcc9zRREWR6Bj_d5f8-QUAapjWx090nsytGtF7q5Nb8w?e=pNcPEw

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
3146279_Dissertation/
│
├── README.md                              ← This file
│
├── medicinal-plant-identification/
│   ├── requirements.txt
│   ├── notebooks/
│   │   ├── Completed Notebooks/
│   │   │   ├── 01_data_exploration.ipynb
│   │   │   ├── 02_phase1_baseline.ipynb
│   │   │   ├── 03_phase2_regional.ipynb
│   │   │   ├── 04_phase3a_endangered.ipynb
│   │   │   ├── 05_phase3b_commercial.ipynb
│   │   │   ├── 06_retrain_improved.ipynb       (EfficientNetB3 training)
│   │   │   ├── 07_dissertation_figures.ipynb
│   │   │   ├── 08_ablation_study.ipynb
│   │   │   ├── 09_dataset3_test_gradcam.ipynb
│   │   │   ├── 10a_18class_reeval.ipynb        (18-class fair evaluation)
│   │   │   ├── 10b_multiseed_ablation.ipynb    (5-seed statistical power)
│   │   │   └── 10c_efficientnet_eval.ipynb     (EfficientNetB3 18-class eval, 99.13%)
│   │   ├── nb06_improved_files/                (EfficientNetB3 model outputs)
│   │   └── phase3b_files/                      (Phase 3b model outputs)
│   ├── webapp/
│   │   ├── app.py
│   │   ├── database.py
│   │   ├── requirements.txt
│   │   ├── templates/
│   │   ├── static/
│   │   └── models/ 
│   └── data/                                   (Datasets - not tracked)
│
├── Dissertation/
│   ├── Hareeshwar_Dissertation.pdf        ← Final dissertation (submitted to Canvas)
│   ├── 3146279_Coversheet.pdf             ← Completed coversheet
│   └── Supplementary_Documents/
│       ├── Appendix_A_User_Guide.pdf
│       └── Appendix_B_Per_Species_Metrics.pdf
│
├── Google_Drive_Backup/                   ← Full backup from Google Drive 
│   ├── models/                            ← Trained model files (.keras, .h5)
│   ├── data/                              ← Dataset folders (or download links)
│   ├── ablation_results/
│   ├── dataset3_results/
│   ├── efficientnet_eval_results/
│   ├── multiseed_ablation_results/
│   └── dissertation_figures/
│
├── Research_Papers/                       ← Referenced literature (PDFs) 
│   ├── Core_References/                   ← Papers directly cited in dissertation
│   │   ├── [5]_Mulugeta_2024_Systematic_Review.pdf
│   │   ├── [7]_Fayek_2020_Progressive_Learning.pdf
│   │   ├── [8]_Siemon_2021_Sequential_Transfer.pdf
│   │   ├── [9]_He_2016_ResNet.pdf
│   │   ├── [24]_Yang_2024_Sequential_Transfer_Path.pdf
│   │   ├── [25]_Kirkpatrick_2017_Catastrophic_Forgetting.pdf
│   │   ├── [37]_Tan_2019_EfficientNet.pdf
│   │   ├── [38]_Selvaraju_2017_GradCAM.pdf
│   │   └── ... (other cited papers)
│   └── Related_Work/                      ← Additional papers reviewed
│       └── ...
│
├── Figures/                               ← All figures used in the dissertation
│   ├── Fig_1.1_Dual_Stakeholder.png
│   ├── Fig_3.1_CRISP_DM.png
│   ├── Fig_3.2_Dataset_Distribution.png
│   ├── Fig_3.3_Sequential_Pipeline.png
│   ├── Fig_3.4_ResNet50_Architecture.png
│   ├── Fig_3.5_Progressive_Unfreezing.png 
│   ├── Fig_4.1_Phase1_Training.png
│   ├── Fig_4.2_Phase2_Training.png
│   ├── Fig_4.3_Phase3a_Training.png
│   ├── Fig_4.4_Phase3b_Training.png
│   ├── Fig_4.5_WebApp_Interface.png
│   ├── Fig_4.6_WebApp_Prediction.png
│   ├── Fig_4.7_OOD_Detection.png
│   ├── Fig_5.1_Confusion_Matrix.png
│   ├── Fig_5.2_F1_Distribution.png
│   ├── Fig_5.3_Accuracy_Progression.png
│   ├── Fig_5.4_Ablation_Comparison.png
│   ├── Fig_5.5_Dataset3_Confidence.png
│   └── Fig_5.6_GradCAM_Maps.png
│
└── Ethics/
    ├── 3146279_Ethics_Form.pdf
    ├── Participant_Information_Sheet.pdf
    ├── Participant_Consent_Form.pdf
    └── User_Testing_Tasks.pdf
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
3. Set runtime to GPU: Runtime -> Change runtime type -> GPU (Runtime type: Python 3, Hardware accelerator: T4 GPU)
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
