 ============================================================
 Google Drive Project Files
 Sequential Transfer Learning for Medicinal Plant Identification
 Hareeshwar Muthukumaran (3146279) | University of Stirling
 ============================================================

 Google Drive Link:
 https://drive.google.com/drive/folders/1RQGF7XmuYf-3XZJV5sNhjfle0h0Ge6FC?usp=sharing

 ============================================================
 This folder contains all training outputs, model artefacts, evaluation results, and figures generated during the project.
 Notebooks that produced these files are in the GitHub repository:  https://github.com/Hareesh-War/3146279-Dissertation
 ============================================================

MedicinalPlant_Dissertation/
│
├── models/                                    # Trained model weights and metadata
│   ├── phase1_baseline.keras                  # Phase 1 model (Dataset 1, 6 species, frozen ResNet50)
│   ├── phase1_class_names.json                # Phase 1 class label mapping
│   ├── phase1_history.json                    # Phase 1 training history (accuracy, loss per epoch)
│   ├── phase2_regional.keras                  # Phase 2 model (Dataset 2, 6 Bangladesh species)
│   ├── phase2_class_names.json                # Phase 2 class label mapping
│   ├── phase2_history.json                    # Phase 2 training history
│   ├── phase3a_endangered.keras               # Phase 3a model (Dataset 4, 16 endangered species)
│   ├── phase3a_class_names.json               # Phase 3a class label mapping
│   ├── phase3a_history.json                   # Phase 3a training history
│   ├── phase3a_species_metrics.json           # Phase 3a per-species precision/recall/F1
│   ├── phase3b_commercial.keras               # Phase 3b model (Dataset 5, 20 commercial species)
│   ├── phase3b_commercial.h5                  # Phase 3b model (.h5 format for Flask web app)
│   ├── phase3b_class_names.json               # Phase 3b class label mapping
│   ├── phase3b_history.json                   # Phase 3b training history
│   ├── phase3b_species_metrics.json           # Phase 3b per-species precision/recall/F1
│   ├── improved_model.keras                   # EfficientNetB3 model (18 species, 99.13% accuracy)
│   ├── improved_model.h5                      # EfficientNetB3 model (.h5 for Flask web app)
│   ├── improved_class_names.json              # EfficientNetB3 class label mapping
│   ├── improved_history.json                  # EfficientNetB3 training history
│   └── improved_species_metrics.json          # EfficientNetB3 per-species metrics
│
├── data/                                      # Training datasets (from Mendeley Data)
│   ├── dataset1/                              # Phase 1: Medicinal Plant Identification (6 species)
│   ├── dataset2/                              # Phase 2: Bangladesh Medicinal Leaves (6 species)
│   ├── dataset3/                              # Independent Test Set: Medicinal Leaf Dataset (9 species)
│   ├── dataset4/                              # Phase 3a: REMP Rare Endangered Plants (16 species)
│   ├── dataset5/                              # Phase 3b: SIMPD South Indian Plants (20 species)
│   ├── dataset1.zip                           # Original download archives
│   ├── dataset2.zip
│   ├── dataset3.zip
│   ├── dataset4.zip
│   └── dataset5.zip
│
├── ablation_results/                          # Notebook 08: Ablation study outputs
│   ├── exp1_direct_best.keras                 # Experiment 1: Direct transfer model (ImageNet -> D5)
│   ├── exp1_direct_history.json               # Experiment 1: Training history
│   ├── exp2_joint_best.keras                  # Experiment 2: Joint training model (all datasets)
│   ├── exp2_joint_history.json                # Experiment 2: Training history
│   ├── ablation_comparison.json               # Summary: Direct 74.46%, Joint 64.52%, Sequential 71.43%
│   └── ablation_comparison.png                # Bar chart comparing three strategies
│
├── multiseed_ablation_results/                # Notebook 10b: Multi-seed statistical replication
│   ├── direct_seed42_best.keras               # Direct transfer trained with seed=42
│   ├── direct_seed42_history.json
│   ├── direct_seed123_best.keras              # Direct transfer trained with seed=123
│   ├── direct_seed123_history.json
│   ├── direct_seed456_best.keras              # Direct transfer trained with seed=456
│   ├── direct_seed456_history.json
│   ├── direct_seed789_best.keras              # Direct transfer trained with seed=789
│   ├── direct_seed789_history.json
│   ├── direct_seed2024_best.keras             # Direct transfer trained with seed=2024
│   ├── direct_seed2024_history.json
│   ├── multiseed_summary.json                 # Mean: 70.00%, Std: 2.74%, Range: 66.02%-73.81%
│   └── multiseed_comparison.png               # Per-seed accuracy chart + sequential comparison
│
├── 18class_eval_results/                      # Notebook 10a: Fair 18-class re-evaluation
│   ├── phase3b_18class_metrics.json           # Sequential pipeline: 71.43% on 18 viable classes
│   ├── phase3b_18class_f1_distribution.png    # F1-score distribution (18 classes)
│   └── phase3b_18class_confusion_matrix.png   # Confusion matrix (18 classes)
│
├── efficientnet_eval_results/                 # Notebook 10c: EfficientNetB3 evaluation
│   ├── efficientnet_18class_metrics.json      # 99.13% accuracy, 99.17% precision, 99.13% recall
│   ├── efficientnet_18class_confusion_matrix.png
│   ├── efficientnet_18class_f1_distribution.png
│   └── improved_species_metrics.json          # Per-species breakdown
│
├── dataset3_results/                          # Notebook 09: Independent test set + Grad-CAM
│   ├── dataset3_results.json                  # 0% accuracy on overlapping species, 81.05% mean confidence
│   ├── dataset3_confidence.png                # Confidence distribution histogram
│   ├── dataset3_confusion_matrix.png          # Prediction distribution across species
│   ├── gradcam_dataset3.png                   # Grad-CAM attention maps (9 species)
│   └── _temp_weights.h5                       # Temporary weights for Grad-CAM extraction
│
├── dissertation_figures/                      # All figures used in the final dissertation
│   ├── Figure 1.1 Dual-Stakeholder Use Case.png
│   ├── Figure 3.1 CRISP-DM Methodology Adapted for This Project.png
│   ├── Figure 3.2 Dataset Distribution Across Training Phases.png
│   ├── Figure 3.3 Sequential Transfer Learning Pipeline.png
│   ├── Figure 3.4 ResNet50 Architecture with Custom Classification Head.png
│   ├── Figure 3.5 Progressive Layer Unfreezing Strategy.png
│   ├── Figure 3.6 Web Application System Architecture.png
│   ├── Figure 4.1 Phase 1 Training Curves.png
│   ├── Figure 4.2 Phase 2 Training Curves.png
│   ├── Figure 4.3 Phase 3a Training Curves (Accuracy, Loss, Precision).png
│   ├── Figure 4.4 Phase 3b Training Curves (Accuracy, Loss, Precision).png
│   ├── Figure 4.5 Web Application Main Interface.png
│   ├── Figure 4.6 Web Application Prediction Result.png
│   ├── Figure 4.7 Working OOD Detection.png
│   ├── Figure 5.1 Phase 3b Confusion Matrix.png
│   ├── Figure 5.2 Per-Species F1-Score Distribution.png
│   ├── Figure 5.3 Training Accuracy Progression Across All Phases.png
│   ├── Figure 5.4a Ablation Comparison (single-seed).png
│   ├── Figure 5.4b Multi-seed comparison.png
│   ├── Figure 5.5 Dataset 3 Confidence Distribution.png
│   └── Figure 5.6 Grad-CAM Attention Maps on Dataset 3 Samples.png
│
├── dataset_config.json                        # Dataset paths and configuration for all notebooks
│
│   # Root-level training visualisations (generated during training)
├── phase1_training_curves.png
├── phase1_confusion_matrix.png
├── phase2_training_curves.png
├── phase2_confusion_matrix.png
├── phase3a_training_curves.png
├── phase3a_confusion_matrix.png
├── phase3b_training_curves.png
├── phase3b_confusion_matrix.png
├── phase3b_confidence_distribution.png
├── improved_training_curves.png
└── improved_confusion_matrix.png

 ============================================================
 NOTEBOOK → OUTPUT MAPPING
 ============================================================
 Notebook 01 (data_exploration)     → dataset_config.json, data/
 Notebook 02 (phase1_baseline)      → models/phase1_*, phase1_*.png
 Notebook 03 (phase2_regional)      → models/phase2_*, phase2_*.png
 Notebook 04 (phase3a_endangered)   → models/phase3a_*, phase3a_*.png
 Notebook 05 (phase3b_commercial)   → models/phase3b_*, phase3b_*.png
 Notebook 06 (retrain_improved)     → models/improved_*, improved_*.png
 Notebook 07 (dissertation_figures) → dissertation_figures/
 Notebook 08 (ablation_study)       → ablation_results/
 Notebook 09 (dataset3_test)        → dataset3_results/
 Notebook 10a (18class_reeval)      → 18class_eval_results/
 Notebook 10b (multiseed_ablation)  → multiseed_ablation_results/
 Notebook 10c (efficientnet_eval)   → efficientnet_eval_results/
