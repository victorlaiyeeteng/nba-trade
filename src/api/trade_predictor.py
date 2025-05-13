from pydantic import BaseModel
import numpy as np
import joblib
import os
import pandas as pd

CLASS_TO_OUTCOME_MAP = {0: "waived", 1: "stayed", 2: "traded"}
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "ml")
MODEL_PATH = os.path.abspath(os.path.join(MODEL_DIR, "trade_predictor.pkl"))
ENCODER_PATH = os.path.abspath(os.path.join(MODEL_DIR, "label_encoder.pkl"))

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

async def predict_trade(player_stat_results):
    if player_stat_results:
        player_stat_df = pd.DataFrame([dict(player_stat_results)])
    else:
        player_stat_df = pd.DataFrame()

    X = player_stat_df.drop(columns=['id', 'playername', 'playerid', 'season', 'team'])
    positions_int_map = {"PG": 0, "SG": 1, "SF": 2, "PF": 3, "C": 4}
    X['position'] = X['position'].apply(lambda x: positions_int_map[x.split('-')[0]] if x else np.nan)
    X = X.reindex(columns=model.feature_names_in_, fill_value=0)

    probabilities = model.predict_proba(X)
    decoded_classes = label_encoder.inverse_transform(model.classes_)

    prediction = CLASS_TO_OUTCOME_MAP[int(decoded_classes[np.argmax(probabilities, axis=1)])]
    outcome_probabilities = {CLASS_TO_OUTCOME_MAP[int(decoded_classes[i])]: float(prob) for i, prob in enumerate(probabilities[0])}

    return prediction, outcome_probabilities



    