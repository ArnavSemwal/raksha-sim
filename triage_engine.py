
"""
import xgboost as xgb
import pandas as pd


try:
    xgb_model = xgb.XGBClassifier()
    xgb_model.load_model('triage_xgboost.json')
except Exception as e:
    print(f"Error loading model: {e}")


TRIAGE_MAP = {0: "Green", 1: "Yellow", 2: "Red"}
RED_FLAG_KEYWORDS = ["dizzy", "chest pain", "fever", "fainting", "blood", "shortness of breath"]


def analyze_patient(sensor_packet: dict) -> dict:
    

    pulse_ox = sensor_packet.get('step_4_pulse_oximetry', {})
    bp = sensor_packet.get('step_3_bp', {})
    

    features = pd.DataFrame([{
        'ecg_hr': pulse_ox.get('heart_rate', 75.0),
        'bp_sys': bp.get('systolic', 120.0),
        'bp_dia': bp.get('diastolic', 80.0),
        'spo2': pulse_ox.get('spo2', 98.0),
        'temperature': sensor_packet.get('step_5_ir_temperature', 37.0),

        'urine_r': 255.0,
        'urine_g': 234.0,
        'urine_b': 112.0
    }])
    
    
    probs = xgb_model.predict_proba(features)[0]
    predicted_class_idx = int(probs.argmax())
    confidence = float(probs[predicted_class_idx])
    ai_triage = TRIAGE_MAP[predicted_class_idx]
    
    
    speech_text = sensor_packet.get('step_7_speech_text', "").lower()
    symptoms = [kw for kw in RED_FLAG_KEYWORDS if kw in speech_text]
    
    
    if symptoms and ai_triage != "Red":
        ai_triage = "Red"
        confidence = 0.99 
        
    return {
        "triage": ai_triage,
        "confidence": round(confidence, 2)
    }

"""


""" code is not good enough as the if statements make the confidence levels not realistic. 
Changes made is to use Ensemble logic where we deal with probabilities and not hardcoding 
.i.e. if there are symptoms, instead of declaring it as Red we are going to 
increse its probability and decrease the probability of green.
"""
import xgboost as xgb
import pandas as pd

try:
    xgb_model = xgb.XGBClassifier()
    xgb_model.load_model('triage_xgboost.json')
except Exception as e:
    print(f"Error loading model: {e}")


TRIAGE_MAP = {0: "Green", 1: "Yellow", 2: "Red"}
RED_FLAG_KEYWORDS = ["dizzy", "chest pain", "fever", "fainting", "blood", "shortness of breath"]


def analyze_patient(sensor_packet: dict) -> dict:

    ecg = sensor_packet.get('ecg', {})
    pulse_ox = sensor_packet.get('pulse_oximeter', {})
    temp = sensor_packet.get('temperature', {})
    urine = sensor_packet.get('urine_sensor', {})
    
    features = pd.DataFrame([{
        'ecg_hr': ecg.get('heart_rate_bpm', 75.0),
        'bp_sys': sensor_packet.get('bp_sys') or 120.0,
        'bp_dia': sensor_packet.get('bp_dia') or 80.0,
        'spo2': pulse_ox.get('spo2_percent', 98.0),
        'temperature': temp.get('body_temp_c', 37.0),
        'urine_r': float(urine.get('red', 255.0)),
        'urine_g': float(urine.get('green', 234.0)),
        'urine_b': float(urine.get('blue', 112.0))
    }])
    

    raw_probs = xgb_model.predict_proba(features)[0]
    p_green, p_yellow, p_red = raw_probs[0], raw_probs[1], raw_probs[2]
    

    speech_text = (sensor_packet.get('patient_speech_text') or "").lower()
    symptoms = [kw for kw in RED_FLAG_KEYWORDS if kw in speech_text]
    

    if symptoms:
        
        p_red += 0.45 
        p_yellow += 0.10
        p_green *= 0.10 
        
        
        total = p_green + p_yellow + p_red
        p_green, p_yellow, p_red = p_green/total, p_yellow/total, p_red/total

    
    final_probs = [p_green, p_yellow, p_red]
    confidence = max(final_probs)
    predicted_class_idx = final_probs.index(confidence)
    
    return {
        "triage": TRIAGE_MAP[predicted_class_idx],
        "confidence": round(confidence, 2)
    }
