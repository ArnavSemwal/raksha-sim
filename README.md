# Raksha Simulator (raksha-sim)

Raksha Simulator is a medical vital monitoring and automated triage system backend and frontend review interface.

## Overview

The backend is powered by FastAPI and SQLite, handling real-time vital ingestion (ECG, SPO2, Body Temperature, Stethoscope status, Urine RGB analysis, and voice-to-text patient feedback) as well as clinical triage classification.

## Hardware Telemetry & AI Model Source
<!-- DATA_SOURCE: https://raksha-sim-1.onrender.com -->
Unified single-source schema mapping hardware telemetry to AI triage model.

## UI Design Screens & Review Flow

UI design screens and interactive design mockups have been added under the [`pages/`](pages/) directory for the clinical and visual review flow. These mockups provide complete HTML implementations, design documentation, and high-fidelity screen mockups (`code.html`, `DESIGN.md`, `screen.png`) for each module:

### Included UI Mockups & Screens:
- **Base Dashboard** ([`pages/BASE`](pages/BASE)): Main vital monitoring dashboard layout and overview.
- **Patient Registration** ([`pages/REGISTER`](pages/REGISTER)): Patient intake and onboarding interface.
- **ECG Monitoring** ([`pages/ECG/1`](pages/ECG/1), [`pages/ECG/2`](pages/ECG/2)): Electrocardiogram waveform visualization and Heart Rate tracking.
- **SPO2 & Temperature** ([`pages/SPO2 + TEMP`](pages/SPO2 + TEMP)): Pulse oximetry saturation and thermal monitoring interface.
- **Stethoscope Audio** ([`pages/STETH/1`](pages/STETH/1), [`pages/STETH/2`](pages/STETH/2)): Cardiac and pulmonary auscultation interface.
- **Urine RGB Analysis** ([`pages/URINE/1`](pages/URINE/1), [`pages/URINE/2`](pages/URINE/2)): Urinalysis colorimetry test screens.
- **Final Summary** ([`pages/FINAL`](pages/FINAL)): Comprehensive patient report and review flow completion.

Each screen folder contains:
- `code.html`: Full interactive HTML/CSS implementation of the UI screen.
- `screen.png`: High-resolution visual mockup image.
- `DESIGN.md`: Structural design guidelines and component specifications.

## API Endpoints

- `GET /`: API health check.
- `POST /vitals`: Ingest patient vitals (ECG HR, SPO2, Temp, Stethoscope status, Urine RGB, Speech text).
- `POST /triage`: Ingest triage classification and confidence score.
- `GET /patients`: Retrieve all stored vitals and triage results.

## Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Running the API

```bash
uvicorn main:app --reload
```

