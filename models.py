from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Vitals(Base):
    __tablename__ = "vitals"
    id = Column(String, primary_key=True) # e.g. patient_id + timestamp
    patient_id = Column(String)
    timestamp = Column(DateTime)
    
    # ECG
    ecg_hr = Column(Integer)
    ecg_samples = Column(JSON) # Storing the array of integers
    
    # Stethoscope
    steth_rms = Column(Integer)
    steth_min = Column(Integer)
    steth_max = Column(Integer)
    steth_samples = Column(Integer)
    
    # Pulse Oximeter
    spo2_percent = Column(Integer)
    spo2_hr = Column(Integer)
    spo2_ir_raw = Column(Integer)
    
    # Temperature
    temperature = Column(Float)
    
    # Urine Colorimetry
    urine_r = Column(Integer)
    urine_g = Column(Integer)
    urine_b = Column(Integer)
    
    # Speech & BP - Kept optional in case the hardware team adds them back
    bp_sys = Column(Float, nullable=True)
    bp_dia = Column(Float, nullable=True)
    patient_speech_text = Column(String, nullable=True)

class Triage(Base):
    __tablename__ = "triage"
    id = Column(String, primary_key=True)
    patient_id = Column(String)
    timestamp = Column(DateTime)
    triage = Column(String) # "Green" / "Yellow" / "Red"
    confidence = Column(Float)