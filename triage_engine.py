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
