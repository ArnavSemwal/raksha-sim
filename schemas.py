from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Nested Sensor Models ---

class ECGData(BaseModel):
    heart_rate_bpm: int
    samples: List[int]

class UrineSensorData(BaseModel):
    red: int
    green: int
    blue: int

class StethoscopeData(BaseModel):
    rms: int
    min: int
    max: int
    samples: int

class TemperatureData(BaseModel):
    body_temp_c: float

class PulseOximeterData(BaseModel):
    heart_rate_bpm: int
    spo2_percent: int
    ir_raw: int

# --- Main API Payloads ---

class VitalsIn(BaseModel):
    device_id: str
    timestamp: str 
    ecg: ECGData
    urine_sensor: UrineSensorData
    stethoscope: StethoscopeData
    temperature: TemperatureData
    pulse_oximeter: PulseOximeterData
    status: str
    
    # Kept optional (default to None) so FastAPI doesn't throw a 422 error 
    # if the hardware team hasn't added these back to the JSON yet.
    patient_id: Optional[str] = None 
    bp_sys: Optional[float] = None
    bp_dia: Optional[float] = None
    patient_speech_text: Optional[str] = None

class TriageIn(BaseModel):
    patient_id: str
    timestamp: datetime
    triage: str
    confidence: float