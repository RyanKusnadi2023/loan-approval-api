#services.py: Model loading, preprocessing, and prediction logic
import pandas as pd

#Load Env and Resources
def load_resources():
    load_dotenv()
    global model, scaler, features
    global gender_map, default_map, education_order, home_ownership_options, loan_intent_options
    #load all these global variables here

load_resources()

#Preprocess Example
def preprocess_input(data: dict, model, scalar, features) -> pd.DataFrame:
    """
    Preprocess raw input data into model-ready DataFrame.
    """
    # TODO: implement actual preprocessing
    return pd.DataFrame([data])

#Predict Example
def predict(df: pd.DataFrame) -> int:
    """
    Make a prediction from preprocessed DataFrame.
    """
    # TODO: implement actual model prediction
    return 0
