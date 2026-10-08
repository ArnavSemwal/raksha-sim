/*
  ============================================================================
  firmware_additions.cpp  — ADDITIVE PATCH for ESP32_VitalsRig.ino
  ============================================================================

  DO NOT replace firmware latest.cpp with this file.
  MERGE these additions into firmware latest.cpp at the marked locations.

  What this adds:
    1. Storage for voice keywords received from Pi (sent by mobile Vosk).
    2. New command handler: "VOICE_KW:<kw1>,<kw2>,..."
    3. New command handler: "SEND_TRIAGE"
       - Assembles the full vitals packet (all 5 readings collected so far)
         + stored voice keywords into a JSON string.
       - POSTs it to the Pi HTTP server via WiFi (ESP32 must have WiFi
         configured — see Section A below).
       - Waits for the Pi's JSON triage response.
       - Sends the triage JSON back to mobile over Serial in the standard
         framed format: "TRIAGE|<json>|<CRC8>\n"

  ============================================================================
  SECTION A — WiFi / HTTP client setup (add to global scope in firmware)
  ============================================================================
  Add these includes at the TOP of firmware latest.cpp:
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>   // Install: "ArduinoJson" by Benoit Blanchon v7.x

/* Add these constants near the other #defines: */

const char* WIFI_SSID     = "YOUR_WIFI_SSID";      // <-- change this
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";   // <-- change this
const char* PI_BASE_URL   = "http://192.168.1.100:8000";  // <-- Pi's LAN IP

/*
  ============================================================================
  SECTION B — Global storage for voice keywords and sensor readings
  ============================================================================
  Add these globals near the other global variables in firmware latest.cpp:
*/

// Voice keywords forwarded from mobile via Pi
char g_voiceKeywords[256] = "";   // stores "fever,chest pain,dizzy" etc.

// Collected sensor readings (filled as each REQ_* completes)
// These mirror the JSON fields the Pi's /run_triage expects.
bool    g_ecgReady    = false;
int     g_ecgHR       = 0;
int     g_ecgSamples[ECG_NUM_SAMPLES];  // reuse existing ecgSamples[]

bool    g_urineReady  = false;
uint16_t g_urineR = 0, g_urineG = 0, g_urineB = 0;

bool    g_stethReady  = false;
int     g_stethRms = 0, g_stethMin = 0, g_stethMax = 0;

bool    g_tempReady   = false;
float   g_tempC       = 0.0f;

bool    g_spo2Ready   = false;
int     g_spo2Hr      = 0;
float   g_spo2Pct     = 0.0f;

/*
  ============================================================================
  SECTION C — WiFi connection helper (add to setup() or as a helper function)
  ============================================================================
*/

void connectWiFi() {
  Serial.print(F("[WiFi] Connecting to "));
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 30) {
    delay(500);
    Serial.print('.');
    retries++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print(F("[WiFi] Connected! IP: "));
    Serial.println(WiFi.localIP());
  } else {
    Serial.println(F("[WiFi] Connection failed. Triage POST will not work."));
  }
}

/*  Call connectWiFi() at the END of setup() in firmware latest.cpp:

      void setup() {
        // ... existing setup code ...
        connectWiFi();           // <-- ADD THIS LINE
        Serial.println(F("[BOOT] Ready."));
      }
*/

/*
  ============================================================================
  SECTION D — Extended handleIncomingCommand()
  ============================================================================
  In firmware latest.cpp, inside handleIncomingCommand(), ADD these two
  else-if branches BEFORE the final else { Unknown command } block:
*/

  // ── NEW: voice keywords forwarded by Pi from mobile Vosk ──
  // Command format: "VOICE_KW:fever,chest pain,dizzy"
  else if (cmd.startsWith("VOICE_KW:")) {
    String kw = cmd.substring(9);   // everything after "VOICE_KW:"
    kw.toCharArray(g_voiceKeywords, sizeof(g_voiceKeywords));
    Serial.print(F("[VOICE] Keywords stored: "));
    Serial.println(g_voiceKeywords);
    // No packet reply needed — just storage.
  }

  // ── NEW: trigger full vitals POST to Pi for AI triage ──
  // Sent by mobile after all 5 readings are collected and voice is done.
  else if (cmd == "SEND_TRIAGE") {
    sendTriageToPi();
  }

/*
  ============================================================================
  SECTION E — Store sensor results after each successful read
  ============================================================================
  In each step*Sequence() function, after sendPacket() and BEFORE
  "currentState = STATE_IDLE;", add the corresponding storage line:

  In stepEcgSequence():
      g_ecgHR = bpm;
      memcpy(g_ecgSamples, ecgSamples, sizeof(ecgSamples));
      g_ecgReady = true;

  In stepUrineSequence():
      g_urineR = r; g_urineG = g; g_urineB = b;
      g_urineReady = true;

  In stepStethSequence() (inside the stethSampleCount >= STETH_NUM_SAMPLES block):
      g_stethRms = rms; g_stethMin = minVal; g_stethMax = maxVal;
      g_stethReady = true;

  In stepTempSequence():
      g_tempC = (float)tempC;
      g_tempReady = true;

  In stepSpo2Sequence() case 2:
      g_spo2Hr  = (int)heartRateValue;
      g_spo2Pct = (float)spo2Value;
      g_spo2Ready = true;
*/

/*
  ============================================================================
  SECTION F — sendTriageToPi() — the new core function
  ============================================================================
  Add this new function to firmware latest.cpp:
*/

void sendTriageToPi() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println(F("[TRIAGE] WiFi not connected. Cannot POST to Pi."));
    sendError("TRIAGE", "wifi_not_connected");
    return;
  }

  // ── Build the JSON payload ──
  // Using ArduinoJson v7 (JsonDocument is the unified type)
  JsonDocument doc;

  if (g_ecgReady) {
    JsonObject ecg = doc["ecg"].to<JsonObject>();
    ecg["heart_rate_bpm"] = g_ecgHR;
    JsonArray samples = ecg["samples"].to<JsonArray>();
    for (int i = 0; i < ECG_NUM_SAMPLES; i++) samples.add(g_ecgSamples[i]);
  }

  if (g_urineReady) {
    JsonObject urine = doc["urine_sensor"].to<JsonObject>();
    urine["red"]   = g_urineR;
    urine["green"] = g_urineG;
    urine["blue"]  = g_urineB;
  }

  if (g_stethReady) {
    JsonObject steth = doc["stethoscope"].to<JsonObject>();
    steth["rms"]     = g_stethRms;
    steth["min"]     = g_stethMin;
    steth["max"]     = g_stethMax;
    steth["samples"] = STETH_NUM_SAMPLES;
  }

  if (g_tempReady) {
    JsonObject temp = doc["temperature"].to<JsonObject>();
    temp["body_temp_c"] = g_tempC;
  }

  if (g_spo2Ready) {
    JsonObject spo2 = doc["pulse_oximeter"].to<JsonObject>();
    spo2["heart_rate_bpm"] = g_spo2Hr;
    spo2["spo2_percent"]   = g_spo2Pct;
  }

  // Voice keywords (stored as a JSON array)
  if (strlen(g_voiceKeywords) > 0) {
    JsonArray kwArray = doc["voice_keywords"].to<JsonArray>();
    // Split CSV into individual keywords
    char tmp[256];
    strncpy(tmp, g_voiceKeywords, sizeof(tmp) - 1);
    char* token = strtok(tmp, ",");
    while (token != nullptr) {
      kwArray.add(String(token));
      token = strtok(nullptr, ",");
    }
  }

  // Default BP (not measured by ESP32 sensors)
  JsonObject bp = doc["step_3_bp"].to<JsonObject>();
  bp["systolic"]  = 120;
  bp["diastolic"] = 80;

  String jsonBody;
  serializeJson(doc, jsonBody);

  // ── POST to Pi ──
  Serial.print(F("[TRIAGE] POSTing to Pi: "));
  Serial.println(jsonBody);

  HTTPClient http;
  String url = String(PI_BASE_URL) + "/run_triage";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(15000);   // 15 s timeout for the AI model

  int httpCode = http.POST(jsonBody);

  if (httpCode == 200) {
    String responseBody = http.getString();
    Serial.print(F("[TRIAGE] Pi response: "));
    Serial.println(responseBody);

    // Forward triage result back to mobile via the existing framed Serial protocol
    // Mobile will read: "TRIAGE|<json>|<CRC8>\n"
    sendPacket("TRIAGE", responseBody);

    // Reset all stored readings so next patient starts fresh
    g_ecgReady = g_urineReady = g_stethReady = g_tempReady = g_spo2Ready = false;
    memset(g_voiceKeywords, 0, sizeof(g_voiceKeywords));
  } else {
    Serial.print(F("[TRIAGE] HTTP error: "));
    Serial.println(httpCode);
    sendError("TRIAGE", "pi_http_error_" + String(httpCode));
  }

  http.end();
}

/*
  ============================================================================
  SUMMARY OF CHANGES NEEDED IN firmware latest.cpp
  ============================================================================
  1. Add includes at top:
       #include <WiFi.h>
       #include <HTTPClient.h>
       #include <ArduinoJson.h>

  2. Add constants (WIFI_SSID, WIFI_PASSWORD, PI_BASE_URL) near other #defines.

  3. Add globals (g_voiceKeywords, g_ecgReady, g_urineR, etc.) near other globals.

  4. Add connectWiFi() function and call it at end of setup().

  5. Add sendTriageToPi() function anywhere before loop().

  6. In handleIncomingCommand(), add the VOICE_KW and SEND_TRIAGE branches
     (Section D above).

  7. In each step*Sequence() function, store readings into the g_* globals
     (Section E above).

  ============================================================================
  MOBILE SIDE — What the Flutter app must do
  ============================================================================
  Reading flow (for each of 5 cards):
    GET http://<PI_IP>:8000/read/<sensor>
    → Display returned JSON in the card.

  Voice flow (after Vosk processes speech):
    POST http://<PI_IP>:8000/voice_keywords
    Body: { "keywords": ["fever", "chest pain"] }
    → Pi forwards to ESP32 as "VOICE_KW:fever,chest pain"

  Triage trigger (after all 5 readings + voice done):
    Mobile sends "SEND_TRIAGE\n" to ESP32 over BLE/Serial
    OR
    Mobile calls GET http://<PI_IP>:8000/triage_result after a short poll delay.

    Preferred flow:
      1. Mobile sends "SEND_TRIAGE" to ESP32 via BLE.
      2. ESP32 calls Pi's /run_triage internally (WiFi).
      3. ESP32 sends result back to mobile via BLE as "TRIAGE|{...}|CRC\n".

  ============================================================================
*/
