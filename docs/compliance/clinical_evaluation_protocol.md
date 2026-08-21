# Raksha Clinical Evaluation Protocol

## 1. Objective
To evaluate the clinical accuracy, reliability, and triage efficacy of the Raksha IoT device and its integrated Edge-AI engine against gold-standard medical equipment in a controlled clinical environment.

## 2. Scope of Testing
- **Vital Sign Accuracy**: Comparison of hardware sensor readings (AD8232 ECG, MAX30102 SpO2, MLX90614 Temperature) against FDA/CDSCO-approved hospital monitors.
- **Triage Efficacy**: Comparison of the Raksha AI + MEWS generated triage status against the independent assessment of two certified medical officers.

## 3. Methodology
### 3.1 Sample Size and Demographics
- Target: 200 human subjects.
- Demographics: Diverse age groups (18-65+), varying BMI, and mixed genders to account for sensor variance (e.g., optical SpO2 skin-tone variance).

### 3.2 Test Procedure
1. Subject is seated and rested for 5 minutes.
2. Standard hospital vitals monitor is attached alongside the Raksha device.
3. Synchronized readings are taken at T=0, T=2m, and T=5m.
4. An independent physician performs a physical examination and logs a manual triage score (Red, Yellow, Green).
5. Raksha's output is logged blindly by a separate technician.

## 4. Acceptance Criteria
- **SpO2 Accuracy**: +/- 2% within the 70-100% range compared to the reference pulse oximeter.
- **Heart Rate Accuracy**: +/- 3 bpm or 3% (whichever is greater).
- **Temperature Accuracy**: +/- 0.2 C.
- **Triage Sensitivity/Specificity**: 
  - >95% sensitivity for detecting "RED" (critical) patients.
  - >90% specificity for detecting "Green" (normal) patients.
  - Zero tolerance for AI false-negatives on critically abnormal raw vitals (mitigated by MEWS).

## 5. Ethical Considerations
The study will be conducted under the approval of an Institutional Ethics Committee (IEC). Informed written consent will be obtained from all participants.
