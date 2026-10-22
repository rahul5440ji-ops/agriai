"""Market price forecasting pipeline for AgriAI (Model B).

This module contains the complete training pipeline for market price
forecasting. Target: modal_price_per_quintal.

The pipeline includes:
1. Data loading and cleaning
2. Feature engineering with lag and rolling features
3. Chronological train/validation split
4. Baseline and ML model training
5. Evaluation with MAE, RMSE, R²
6. Forecast uncertainty handling
7. Model saving and versioning

This code is ONLY for training. Inference is handled by
backend/ml/inference.py which loads the saved artifact.
"""