import joblib
import yaml
import pandas as pd
import logging 

# Define global variables
model: object = None
scaler: object = None
features: list[str] = []
gender_map: dict[str, int] = {}
default_map: dict[str, int] = {}
education_order: dict[str, int] = {}
home_ownership_options: list[str] = []
loan_intent_options: list[str] = []

def load_resources(logger: logging.Logger) -> None:
    """
    Loads model, scaler, features, and configuration.
    """

    global model, scaler, features
    global gender_map, default_map, education_order, home_ownership_options, loan_intent_options

    logger.debug("Starting to load model, scaler, and feature files.")
    try:
        model = joblib.load('models/xgb_model.pkl')
        scaler = joblib.load('models/scaler.pkl')
        features = joblib.load('models/feature_names.pkl')
        logger.info("Model, scaler, and features loaded successfully.")
    except FileNotFoundError as e:
        logger.error("One or more model files not found: %s", e)
        raise
    except (ValueError, TypeError) as e:
        logger.error("Model file content is invalid or corrupted: %s", e)
        raise
    except Exception as e:
        logger.exception("Unexpected error while loading model resources.")
        raise

    logger.debug("Starting to load YAML configuration.")
    try:
        with open("models/config.yaml", "r") as f:
            config = yaml.safe_load(f)

        gender_map = config["gender_map"]
        default_map = config["default_map"]
        education_order = config["education_order"]
        home_ownership_options = config["home_ownership_options"]
        loan_intent_options = config["loan_intent_options"]

        logger.info("Configuration loaded successfully from config.yaml.")
    except FileNotFoundError as e:
        logger.error("Configuration file 'config.yaml' not found: %s", e)
        raise
    except KeyError as e:
        logger.error("Missing expected key in config.yaml: %s", e)
        raise
    except yaml.YAMLError as e:
        logger.error("YAML parsing error in config.yaml: %s", e)
        raise
    except Exception as e:
        logger.exception("Unexpected error while loading configuration.")
        raise

def preprocess_input(input_data: dict, logger: logging.Logger) -> pd.DataFrame:
    """
    Converts raw user input into a DataFrame suitable for prediction.
    """
    logger.debug("Starting preprocessing with input data: %s", input_data)

    try:
        df = pd.DataFrame([input_data])
        logger.debug("Initial DataFrame: %s", df)
    except Exception as e:
        logger.exception("Failed to convert input_data to DataFrame.")
        raise ValueError(f"Invalid input data format: {e}")

    try:
        df['person_gender'] = df['person_gender'].map(gender_map)
        df['previous_loan_defaults_on_file'] = df['previous_loan_defaults_on_file'].map(default_map)
        df['person_education'] = df['person_education'].map(education_order)
        logger.debug("DataFrame after categorical mapping: %s", df)
    except KeyError as e:
        logger.error("Missing key during categorical mapping: %s", e)
        raise ValueError(f"Missing required field: {e}")
    except Exception as e:
        logger.exception("Unexpected error during categorical mapping.")
        raise ValueError(f"Categorical mapping failed: {e}")

    try:
        for col in home_ownership_options[1:]:
            df[f'person_home_ownership_{col}'] = (input_data['person_home_ownership'] == col) * 1
        for col in loan_intent_options[1:]:
            df[f'loan_intent_{col}'] = (input_data['loan_intent'] == col) * 1
        logger.debug("DataFrame after one-hot encoding: %s", df)
    except KeyError as e:
        logger.error("Missing key for one-hot encoding: %s", e)
        raise ValueError(f"Missing field for encoding: {e}")
    except Exception as e:
        logger.exception("Unexpected error during one-hot encoding.")
        raise ValueError(f"One-hot encoding failed: {e}")

    try:
        df = df.drop(['person_home_ownership', 'loan_intent'], axis=1)
    except KeyError as e:
        logger.warning("Column to drop not found, skipping: %s", e)

    try:
        df = df.reindex(columns=features, fill_value=0)
        logger.debug("Final preprocessed DataFrame ready for prediction: %s", df)
    except Exception as e:
        logger.exception("Reindexing failed.")
        raise ValueError(f"Reindexing failed: {e}")

    logger.info("Input data preprocessed successfully.")
    return df

def predict(df: pd.DataFrame, logger: logging.Logger) -> dict[str, float | int]:
    """
    Scales and predicts using the preloaded model.
    """
    logger.debug("Starting prediction with DataFrame: %s", df)

    try:
        scaled = scaler.transform(df)
        probs = model.predict_proba(scaled)[0]
        pred_class = int(probs.argmax())
        confidence = float(probs[pred_class])

        logger.info(f"Prediction successful: Class {pred_class} (confidence: {confidence:.4f})")

        return {
            "prediction": pred_class,
            "confidence": confidence
        }
    except ValueError as e:
        logger.error("Value error during prediction: %s", e)
        raise RuntimeError(f"Invalid input for prediction: {e}")
    except AttributeError as e:
        logger.error("Model or scaler not properly loaded: %s", e)
        raise RuntimeError(f"Model state error: {e}")
    except Exception as e:
        logger.exception("Unexpected error during prediction.")
        raise RuntimeError(f"Prediction failed: {e}")
