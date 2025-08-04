#services.py: Model loading, preprocessing, and prediction logic
import pandas as pd

"""
Model, scalar, features will be loaded in main and injected into services function as a parameter. Remove if not needed.

model = joblib.load('model/xgb_model.pkl')
scaler = joblib.load('model/scaler.pkl')
features = joblib.load('model/feature_names.pkl')

Example of how it will be used in the main:
preprocess_input(data, model, scalar, features)
"""

def preprocess_input(data: dict, model, scalar, features) -> pd.DataFrame:
    """
    Preprocess raw input data into model-ready DataFrame.
    """
    # TODO: implement actual preprocessing
    return pd.DataFrame([data])


def predict(df: pd.DataFrame, model, scalar, features) -> int:
    """
    Make a prediction from preprocessed DataFrame.
    """
    # TODO: implement actual model prediction
    return 0
