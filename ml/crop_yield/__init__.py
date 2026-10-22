"""Yield model training pipeline for AgriAI.

This module contains the complete training pipeline for Model A:
crop yield prediction (target: yield_tonnes_per_hectare).

The pipeline includes:
1. Data loading and cleaning
2. Feature engineering
3. Time-aware train/validation split
4. Baseline and ML model training
5. Evaluation with MAE, RMSE, R²
6. Feature importance / SHAP
7. Model saving and versioning

This code is ONLY for training. Inference is handled by
backend/ml/inference.py which loads the saved artifact.
"""