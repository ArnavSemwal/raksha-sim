# CDSCO Classification for Raksha (Software as a Medical Device)

## 1. Executive Summary
Raksha (SwasthaGram) is a low-cost IoT + Edge-AI health triage device designed for rural healthcare workers (ASHAs/ANMs/PHCs) in India. The system includes an Edge-AI inference engine that processes physiological data (ECG, SpO2, Temperature, Blood Pressure) to classify patients into standard medical triage categories. Under the Central Drugs Standard Control Organisation (CDSCO) guidelines, Raksha qualifies as Software as a Medical Device (SaMD).

## 2. Intended Use
Raksha is intended to be used as a clinical decision support system (CDSS) for preliminary health screening and triage in resource-constrained settings. It is **not** intended to replace a physician's diagnosis. The system alerts frontline health workers to critical abnormalities that require immediate escalation to a medical officer.

## 3. Regulatory Classification Rationale
According to the Medical Devices Rules (MDR) 2017 and the CDSCO's draft guidelines on SaMD:
- **Device Type**: Active diagnostic medical device.
- **Risk Class**: **Class B (Low-Moderate Risk)**.
- **Justification**: The software provides information used to take clinical decisions. The clinical situations are non-critical initially (primary screening), but misclassification could lead to delayed care for edge-case patients. The integration of the MEWS (Modified Early Warning Score) system serves as a deterministic safety fallback to mitigate the risk of AI false negatives, justifying a Class B classification rather than Class C.

## 4. Safety and Performance Requirements
- **Clinical Validation**: The Random Forest triage model must be validated against a curated, localized clinical dataset.
- **Deterministic Overrides**: The MEWS module serves as a mandatory rule-based overlay to prevent AI hallucinations or dangerous misclassifications of critical vital signs.
- **Quality Management**: Adherence to ISO 13485 (QMS for Medical Devices) and IEC 62304 (Medical Device Software Lifecycle) principles during development.
