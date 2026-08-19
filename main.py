from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Vitals, Triage
import schemas

# 1. Database Setup
engine = create_engine("sqlite:///raksha.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. FastAPI Initialization
app = FastAPI(title="Raksha Minimal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://raksha-dash-9dt6-7n5zx41ts-anushka21.vercel.app",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "API is live and database is connected!"}

# 3. Endpoints
@app.post("/vitals")
def add_vitals(v: schemas.VitalsIn, db: Session = Depends(get_db)):
    # Combine patient_id and timestamp to make a unique ID string
    record_id = f"{v.patient_id}_{v.timestamp.isoformat()}"
    
    db_vitals = Vitals(
        id=record_id,
        patient_id=v.patient_id,
        timestamp=v.timestamp,
        stethoscope_status=v.stethoscope_status,
        ecg_hr=v.ecg_hr,
        bp_sys=v.bp_sys,
        bp_dia=v.bp_dia,
        spo2=v.spo2,
        temperature=v.temperature,
        # Splitting the incoming array into 3 separate database columns
        urine_r=v.urine_rgb[0] if len(v.urine_rgb) > 0 else 0.0,
        urine_g=v.urine_rgb[1] if len(v.urine_rgb) > 1 else 0.0,
        urine_b=v.urine_rgb[2] if len(v.urine_rgb) > 2 else 0.0,
        patient_speech_text=v.patient_speech_text
    )
    db.add(db_vitals)
    db.commit()
    return {"message": "Vitals saved successfully", "id": record_id}

@app.post("/triage")
def add_triage(t: schemas.TriageIn, db: Session = Depends(get_db)):
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

@app.get("/patients")
def list_patients(db: Session = Depends(get_db)):
    # Fetches all records so your dashboard can map them together
    vitals = db.query(Vitals).all()
    triages = db.query(Triage).all()
    return {"vitals": vitals, "triage_results": triages}