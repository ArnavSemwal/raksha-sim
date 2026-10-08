"""
Raksha Pi — Hardware Proxy + AI Triage API
==========================================

Architecture (new flow):
  1. Mobile  ──GET /read/<sensor>──►  Pi  ──REQ_*──► ESP32 ──► Pi ──► Mobile
  2. Mobile  ──POST /voice_keywords──► Pi  ──VOICE_KW:<kw1,kw2>──► ESP32
  3. ESP32   ──POST /run_triage──►    Pi   (full sensor + voice packet)
     Pi runs XGBoost triage, stores result.
  4. Mobile  ──GET /triage_result──►  Pi   (polls for last computed result)

hardware_reader.py is unchanged.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import threading

from hardware_reader import ESP32Reader
from triage_engine import analyze_patient

# ---------------------------------------------------------------------------
# App + CORS
# ---------------------------------------------------------------------------
app = FastAPI(title="Raksha Pi — Hardware Proxy & AI Triage API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Hardware reader (one shared Serial instance)
# ---------------------------------------------------------------------------
esp32 = ESP32Reader(port="/dev/ttyACM0")

@app.on_event("startup")
def startup_event():
    esp32.connect()

@app.on_event("shutdown")
def shutdown_event():
    esp32.disconnect()

# ---------------------------------------------------------------------------
# In-memory store for the latest triage result
# ---------------------------------------------------------------------------
_latest_triage: Optional[dict] = None
_triage_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class VoiceKeywordsRequest(BaseModel):
    """Mobile sends extracted Vosk keywords to be forwarded to ESP32."""
    keywords: List[str]

class FullVitalsPacket(BaseModel):
    """
    ESP32 POSTs this after collecting all 5 readings + voice keywords.
    Field names mirror what triage_integrator.parse_sensor_packet() expects.
    """
    ecg: Optional[dict] = None            # {"heart_rate_bpm": int, "samples": [...]}
    urine_sensor: Optional[dict] = None   # {"red": int, "green": int, "blue": int}
    stethoscope: Optional[dict] = None    # {"rms": int, "min": int, "max": int, "samples": int}
    temperature: Optional[dict] = None    # {"body_temp_c": float}
    pulse_oximeter: Optional[dict] = None # {"heart_rate_bpm": int, "spo2_percent": float}
    voice_keywords: Optional[List[str]] = []
    step_3_bp: Optional[dict] = {"systolic": 120, "diastolic": 80}

# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------
@app.get("/")
def read_root():
    return {"status": "Raksha Pi Hardware Proxy & AI Triage API is live!"}

# ---------------------------------------------------------------------------
# STEP 1 — Individual sensor reads
# Mobile taps card ──► Pi ──► ESP32 ──► Pi ──► Mobile
# ---------------------------------------------------------------------------
@app.get("/read/temperature")
def read_temperature():
    """Mobile taps Temperature card -> Pi requests ESP32 -> returns reading."""
    data = esp32.read_sensor("REQ_TEMP")
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    return data

@app.get("/read/urine")
def read_urine():
    """Mobile taps Urine card -> Pi requests ESP32 -> returns reading."""
    data = esp32.read_sensor("REQ_URINE")
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    return data

@app.get("/read/ecg")
def read_ecg():
    """Mobile taps ECG card -> Pi requests ESP32 -> returns reading."""
    data = esp32.read_sensor("REQ_ECG")
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    return data

@app.get("/read/spo2")
def read_spo2():
    """Mobile taps SpO2 card -> Pi requests ESP32 -> returns reading."""
    data = esp32.read_sensor("REQ_SPO2")
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    return data

@app.get("/read/steth")
def read_steth():
    """Mobile taps Stethoscope card -> Pi requests ESP32 -> returns reading."""
    data = esp32.read_sensor("REQ_STETH")
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    return data

# ---------------------------------------------------------------------------
# STEP 2 — Voice keywords relay
# Mobile (Vosk) ──POST /voice_keywords──► Pi ──VOICE_KW:<csv>──► ESP32
# ---------------------------------------------------------------------------
@app.post("/voice_keywords")
def send_voice_keywords(req: VoiceKeywordsRequest):
    """
    After on-device Vosk processes speech, mobile POSTs extracted symptom
    keywords here. Pi forwards them to ESP32 as a single Serial command
    so ESP32 can bundle them into the final vitals packet it sends to /run_triage.

    ESP32 firmware must handle: 'VOICE_KW:<kw1>,<kw2>,...'
    """
    if not req.keywords:
        raise HTTPException(status_code=400, detail="No keywords provided.")

    csv_keywords = ",".join(req.keywords)
    command = f"VOICE_KW:{csv_keywords}"
    esp32.send_raw_command(command)

    return {
        "status": "forwarded",
        "keywords_sent": req.keywords,
        "command_sent_to_esp32": command
    }

# ---------------------------------------------------------------------------
# STEP 3 — AI Triage trigger
# ESP32 ──POST /run_triage──► Pi (full packet) ──► triage result stored + returned
# ---------------------------------------------------------------------------
@app.post("/run_triage")
def run_triage(packet: FullVitalsPacket):
    """
    ESP32 POSTs the fully assembled sensor packet (all 5 readings + voice
    keywords) once it has collected everything. Pi runs the XGBoost triage
    engine and stores the result. The result is also returned in the response
    so ESP32 can immediately route it back to mobile.
    """
    sensor_packet: dict = {}

    if packet.ecg:
        sensor_packet["ecg"] = packet.ecg
    if packet.urine_sensor:
        sensor_packet["urine_sensor"] = packet.urine_sensor
    if packet.stethoscope:
        sensor_packet["stethoscope"] = packet.stethoscope
    if packet.temperature:
        sensor_packet["temperature"] = packet.temperature
    if packet.pulse_oximeter:
        sensor_packet["pulse_oximeter"] = packet.pulse_oximeter
    if packet.step_3_bp:
        sensor_packet["step_3_bp"] = packet.step_3_bp

    # Voice keywords -> feed as symptom text to triage engine
    if packet.voice_keywords:
        sensor_packet["patient_speech_text"] = " ".join(packet.voice_keywords)

    try:
        result = analyze_patient(sensor_packet)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage engine error: {str(e)}")

    global _latest_triage
    with _triage_lock:
        _latest_triage = result

    # ESP32 receives this result immediately and routes it to mobile
    return result

# ---------------------------------------------------------------------------
# STEP 4 — Mobile polls for triage result
# Pi ──GET /triage_result──► Mobile
# ---------------------------------------------------------------------------
@app.get("/triage_result")
def get_triage_result():
    """
    Mobile polls this endpoint (or ESP32 pushes the response it received from
    /run_triage directly). Returns the last triage result computed by Pi.
    """
    with _triage_lock:
        if _latest_triage is None:
            raise HTTPException(
                status_code=404,
                detail="No triage result yet. Waiting for ESP32 to post to /run_triage."
            )
        return _latest_triage

# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------
@app.get("/ping")
def ping():
    """Liveness check: confirms Pi API is up and ESP32 Serial link is alive."""
    esp32_alive = esp32.ping()
    return {"api": "ok", "esp32_connected": esp32_alive}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
