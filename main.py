from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import traceback

from models import Base, Vitals, Triage
import schemas

from triage_engine import analyze_patient 
from mews_check import check_mews

# 1. Database Setup
engine = create_engine("sqlite:///raksha.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. FastAPI Initialization
app = FastAPI(title="Raksha Minimal API")

# Updated CORS per PRD Task 5: Keeping only "*" for hackathon simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "API is live and database is connected!"}

# 3. Endpoints

@app.post("/vitals")
def add_vitals(v: schemas.VitalsIn, db: Session = Depends(get_db)):
    try:
        p_id = v.patient_id if v.patient_id else v.device_id
        current_time = datetime.utcnow()
        record_id = f"{p_id}_{current_time.isoformat()}"
        
        db_vitals = Vitals(
            id=record_id,
            patient_id=p_id,
            timestamp=current_time,
            ecg_hr=v.ecg.heart_rate_bpm,
            ecg_samples=v.ecg.samples,
            steth_rms=v.stethoscope.rms,
            steth_min=v.stethoscope.min,
            steth_max=v.stethoscope.max,
            steth_samples=v.stethoscope.samples,
            spo2_percent=v.pulse_oximeter.spo2_percent,
            spo2_hr=v.pulse_oximeter.heart_rate_bpm,
            spo2_ir_raw=v.pulse_oximeter.ir_raw,
            temperature=v.temperature.body_temp_c,
            urine_r=v.urine_sensor.red,
            urine_g=v.urine_sensor.green,
            urine_b=v.urine_sensor.blue,
            bp_sys=v.bp_sys,
            bp_dia=v.bp_dia,
            patient_speech_text=v.patient_speech_text
        )
        
        db.add(db_vitals)
        db.commit()

        return {
            "message": "Vitals saved successfully", 
            "id": record_id
        }
    except Exception as e:
        db.rollback()
        print(f"Error processing vitals: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Garbled packet or processing error: {str(e)}")

@app.post("/analyze")
def analyze_vitals(v: schemas.VitalsIn, db: Session = Depends(get_db)):
    try:
        p_id = v.patient_id if v.patient_id else v.device_id
        current_time = datetime.utcnow()
        record_id = f"{p_id}_{current_time.isoformat()}"

        try:
            ai_result = analyze_patient(v.dict()) 
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
            
        final_triage_result = ai_result["triage"]
        confidence = ai_result["confidence"]
        
        mews_result = check_mews(v.dict())
        if mews_result["override"]:
            final_triage_result = mews_result["status"].capitalize()
        
        db_triage = Triage(
            id=record_id,
            patient_id=p_id,
            timestamp=current_time,
            triage=final_triage_result,
            confidence=confidence
        )
        db.add(db_triage)
        db.commit()

        return {
            "message": "Analysis completed successfully", 
            "id": record_id,
            "triage_status": final_triage_result,
            "confidence": confidence
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error processing analysis: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Processing error: {str(e)}")

@app.post("/triage")
def add_triage(t: schemas.TriageIn, db: Session = Depends(get_db)):
    '''
    Backward compatibility endpoint for manually recording triage results.
    For real inference, use /analyze.
    '''
    try:
        record_id = f"{t.patient_id}_{t.timestamp.isoformat()}"
        db_triage = Triage(
            id=record_id,
            patient_id=t.patient_id,
            timestamp=t.timestamp,
            triage=t.triage,
            confidence=t.confidence
        )
        db.add(db_triage)
        db.commit()
        return {"message": "Triage saved successfully", "id": record_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
@app.get("/patients")
def list_patients(limit: int = 50, db: Session = Depends(get_db)):
    vitals = (
        db.query(Vitals)
        .order_by(Vitals.timestamp.desc())
        .limit(limit)
        .all()
    )
    triages = (
        db.query(Triage)
        .order_by(Triage.timestamp.desc())
        .limit(limit)
        .all()
    )
    return {"vitals": vitals, "triage_results": triages}