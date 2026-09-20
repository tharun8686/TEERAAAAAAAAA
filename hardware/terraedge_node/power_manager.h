// ============================================================================
// TerraEdge Phase 9 — Field Node Autonomous Power Management Interface
// Modular hardware abstraction layer for ESP32-S3 sensor power rails,
// warm-up scheduling, battery ADC sensing, and adaptive LoRa duty cycling.
//
// PHYSICAL VALIDATION STATUS: HARDWARE-VALIDATION-PENDING
// Load-switch GPIOs and deep-sleep currents are ready for physical MOSFET
// circuit attachment once the manufactured board arrives.
// ============================================================================

#pragma once
#include <Arduino.h>

// ----------------------------------------------------------------------------
// 1. Switched Sensor Power Rail GPIOs (Modular MOSFET / Load Switch Controls)
// ----------------------------------------------------------------------------
// Note: When physical board arrives, these connect to P-channel MOSFET gates.
#define SENSOR_POWER_MQ135      38   // Switched 5V heater rail for MQ-135
#define SENSOR_POWER_SDS011     39   // Switched 5V fan rail for SDS011 PM sensor
#define SENSOR_POWER_PH         40   // Switched 3.3V analog rail for pH probe
#define SENSOR_POWER_TDS        41   // Switched 3.3V analog rail for TDS probe
#define SENSOR_POWER_TURBIDITY  42   // Switched 5V optical rail for Turbidity probe
#define SENSOR_POWER_GPS        48   // Switched 3.3V rail for NEO-6M GPS module
#define SENSOR_POWER_OTHER      46   // Auxiliary sensor switched rail

// ----------------------------------------------------------------------------
// 2. Power States and Default Transmission Intervals (Milliseconds)
// ----------------------------------------------------------------------------
enum PowerState {
  STATE_NORMAL = 0,    // 300 seconds (5 min) — Aggressive sleep, heavy sensors duty-cycled
  STATE_WATCH = 1,     // 60 seconds  (1 min) — Elevated awareness
  STATE_WARNING = 2,   // 30 seconds          — High-frequency monitoring
  STATE_CRITICAL = 3   // 10 seconds          — Continuous emergency tracking
};

#define INTERVAL_NORMAL_MS    300000UL   // 300s
#define INTERVAL_WATCH_MS     60000UL    // 60s
#define INTERVAL_WARNING_MS   30000UL    // 30s
#define INTERVAL_CRITICAL_MS  10000UL    // 10s

// ----------------------------------------------------------------------------
// 3. Battery Voltage & ADC Calibration Constants (2x 18650 parallel pack)
// ----------------------------------------------------------------------------
#ifndef BATTERY_ADC_PIN
#define BATTERY_ADC_PIN       0          // GPIO 0 connected to voltage divider
#endif

#define BATTERY_V_MAX         4.20f
#define BATTERY_V_NOMINAL     3.70f
#define BATTERY_V_MIN         3.00f
#define BATTERY_DIVIDER_RATIO 2.00f      // R1 = 100k, R2 = 100k
#define ADC_REF_VOLTAGE       3.30f
#define ADC_MAX_COUNT         4095.0f

// ----------------------------------------------------------------------------
// 4. Power Manager Class
// ----------------------------------------------------------------------------
class FieldNodePowerManager {
public:
  PowerState currentState;
  int consecutiveNormalSamples;
  unsigned long lastEscalationMillis;
  bool emergencyActive;

  FieldNodePowerManager()
    : currentState(STATE_NORMAL),
      consecutiveNormalSamples(0),
      lastEscalationMillis(0),
      emergencyActive(false) {}

  void init() {
    // Configure switched power rail pins as OUTPUT
    pinMode(SENSOR_POWER_MQ135, OUTPUT);
    pinMode(SENSOR_POWER_SDS011, OUTPUT);
    pinMode(SENSOR_POWER_PH, OUTPUT);
    pinMode(SENSOR_POWER_TDS, OUTPUT);
    pinMode(SENSOR_POWER_TURBIDITY, OUTPUT);
    pinMode(SENSOR_POWER_GPS, OUTPUT);
    pinMode(SENSOR_POWER_OTHER, OUTPUT);

    // Default: Turn off high-power switched sensors at boot
    powerOffAllRails();
    Serial.println("[POWER] Phase 9 Power Manager Initialized (Hardware-Ready)");
  }

  void powerOnSensor(int railPin) {
    digitalWrite(railPin, HIGH);  // Enable MOSFET switch
  }

  void powerOffSensor(int railPin) {
    digitalWrite(railPin, LOW);   // Disable MOSFET switch
  }

  void powerOffAllRails() {
    powerOffSensor(SENSOR_POWER_MQ135);
    powerOffSensor(SENSOR_POWER_SDS011);
    powerOffSensor(SENSOR_POWER_PH);
    powerOffSensor(SENSOR_POWER_TDS);
    powerOffSensor(SENSOR_POWER_TURBIDITY);
    powerOffSensor(SENSOR_POWER_GPS);
    powerOffSensor(SENSOR_POWER_OTHER);
  }

  // Non-blocking warm-up prepare hook
  void prepareSensor(const char* sensorName, unsigned long warmupMs) {
    if (strcmp(sensorName, "sds011") == 0) {
      powerOnSensor(SENSOR_POWER_SDS011);
    } else if (strcmp(sensorName, "mq135") == 0) {
      powerOnSensor(SENSOR_POWER_MQ135);
    } else if (strcmp(sensorName, "gps") == 0) {
      powerOnSensor(SENSOR_POWER_GPS);
    } else if (strcmp(sensorName, "water_quality") == 0) {
      powerOnSensor(SENSOR_POWER_PH);
      powerOnSensor(SENSOR_POWER_TDS);
      powerOnSensor(SENSOR_POWER_TURBIDITY);
    }
  }

  void releaseSensor(const char* sensorName) {
    if (strcmp(sensorName, "sds011") == 0) {
      powerOffSensor(SENSOR_POWER_SDS011);
    } else if (strcmp(sensorName, "mq135") == 0) {
      powerOffSensor(SENSOR_POWER_MQ135);
    } else if (strcmp(sensorName, "gps") == 0) {
      powerOffSensor(SENSOR_POWER_GPS);
    } else if (strcmp(sensorName, "water_quality") == 0) {
      powerOffSensor(SENSOR_POWER_PH);
      powerOffSensor(SENSOR_POWER_TDS);
      powerOffSensor(SENSOR_POWER_TURBIDITY);
    }
  }

  // Battery ADC measurement
  float readBatteryVoltage() {
    uint32_t raw = analogRead(BATTERY_ADC_PIN);
    float pinV = (raw * ADC_REF_VOLTAGE) / ADC_MAX_COUNT;
    float vBat = pinV * BATTERY_DIVIDER_RATIO;
    return vBat;
  }

  float estimateBatterySoc(float vBat) {
    if (vBat >= BATTERY_V_MAX) return 100.0f;
    if (vBat <= BATTERY_V_MIN) return 0.0f;
    // Linear approximation
    return ((vBat - BATTERY_V_MIN) / (BATTERY_V_MAX - BATTERY_V_MIN)) * 100.0f;
  }

  // Deterministic state machine update with hysteresis
  PowerState updateState(float riskPct, bool isEmergency) {
    emergencyActive = isEmergency;
    if (isEmergency) {
      currentState = STATE_CRITICAL;
      consecutiveNormalSamples = 0;
      lastEscalationMillis = millis();
      return currentState;
    }

    PowerState targetState;
    if (riskPct >= 80.0f) {
      targetState = STATE_CRITICAL;
    } else if (riskPct >= 60.0f) {
      targetState = STATE_WARNING;
    } else if (riskPct >= 40.0f) {
      targetState = STATE_WATCH;
    } else {
      targetState = STATE_NORMAL;
    }

    // Escalation (instant)
    if (targetState > currentState) {
      currentState = targetState;
      consecutiveNormalSamples = 0;
      lastEscalationMillis = millis();
      return currentState;
    }

    // Maintained
    if (targetState == currentState) {
      consecutiveNormalSamples = 0;
      return currentState;
    }

    // De-escalation (hysteresis: requires 3 samples and 180s stabilization)
    consecutiveNormalSamples++;
    unsigned long elapsedSinceEsc = (millis() - lastEscalationMillis) / 1000UL;
    if (consecutiveNormalSamples >= 3 && elapsedSinceEsc >= 180UL) {
      if (currentState == STATE_CRITICAL) currentState = STATE_WARNING;
      else if (currentState == STATE_WARNING) currentState = STATE_WATCH;
      else currentState = STATE_NORMAL;

      consecutiveNormalSamples = 0;
      lastEscalationMillis = millis();
    }
    return currentState;
  }

  unsigned long getIntervalMs() {
    switch (currentState) {
      case STATE_CRITICAL: return INTERVAL_CRITICAL_MS;
      case STATE_WARNING:  return INTERVAL_WARNING_MS;
      case STATE_WATCH:    return INTERVAL_WATCH_MS;
      case STATE_NORMAL:
      default:             return INTERVAL_NORMAL_MS;
    }
  }

  const char* getStateString() {
    switch (currentState) {
      case STATE_CRITICAL: return "CRITICAL";
      case STATE_WARNING:  return "WARNING";
      case STATE_WATCH:    return "WATCH";
      case STATE_NORMAL:
      default:             return "NORMAL";
    }
  }
};

extern FieldNodePowerManager NodePower;
