# Digital Personal Data Protection (DPDP) Act Compliance

## 1. Data Architecture & PII Minimization
Raksha processes sensitive Personal Identifiable Information (PII) and Personal Health Information (PHI). To comply with India's DPDP Act (2023):
- **Data Minimization**: The API accepts `patient_id` as a pseudonymized UUID rather than raw names/Aadhaar numbers where possible.
- **Data Residency**: All cloud data is hosted on servers physically located within India (Render/AWS ap-south-1).
- **Encryption**: Data in transit is secured via TLS 1.2/1.3.

## 2. Patient Consent Flow
Prior to capturing physiological data via the Raksha hardware, the ASHA/ANM must verbally and physically capture patient consent on the accompanying mobile/web dashboard.

### 2.1 Notice Requirements
The patient must be informed in their local language:
1. What data is being collected (ECG, SpO2, Temperature).
2. The purpose of collection (health triage and doctor escalation).
3. The identity of the Data Fiduciary (the PHC or implementing NGO).
4. Their right to withdraw consent and request data deletion.

### 2.2 Explicit Consent Text (English & Hindi Drafts)

**English:**
> "I consent to the collection of my vital signs by the Raksha device for the purpose of health screening. I understand this data will be securely processed to evaluate my health status and may be shared with a doctor for further treatment. I have the right to request deletion of this record at any time."

**Hindi (हिंदी):**
> "मैं स्वास्थ्य जांच के उद्देश्य से रक्षा उपकरण द्वारा अपने महत्वपूर्ण संकेतों (vitals) को एकत्र करने की सहमति देता/देती हूँ। मैं समझता/समझती हूँ कि मेरे स्वास्थ्य की स्थिति का मूल्यांकन करने के लिए इस डेटा को सुरक्षित रूप से प्रोसेस किया जाएगा और आगे के इलाज के लिए डॉक्टर के साथ साझा किया जा सकता है। मुझे किसी भी समय इस रिकॉर्ड को हटाने का अनुरोध करने का अधिकार है।"

## 3. Data Principal Rights Management
The dashboard includes an administrative panel allowing the PHC to:
- Export a patient's complete vital history (Right to Data Portability).
- Permanently erase a patient's record from the SQLite database upon request (Right to Erasure).
