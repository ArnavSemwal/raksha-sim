from pydantic import BaseModel
from datetime import datetime

class VitalsIn(BaseModel):
    patient_id: str
    timestamp: datetime
    stethoscope_status: str
    ecg_hr: float
    bp_sys: float
    bp_dia: float
    spo2: float
    temperature: float
    urine_rgb: list[float]
    patient_speech_text: str

class TriageIn(BaseModel):
    patient_id: str
    timestamp: datetime
    triage: str
    confidence: float