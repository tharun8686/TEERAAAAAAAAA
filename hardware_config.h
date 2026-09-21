#pragma once
// Select the actual board in Arduino IDE; pins below are GPIO numbers.
// Enable only physically connected probes. See docs/HARDWARE_TO_DASHBOARD.md.
#define ENABLE_MQ135 true
#define ENABLE_RAIN_PLATE true
#define ENABLE_WATER_ADC true
#define ENABLE_SOIL true
#define ENABLE_PH true
#define ENABLE_TDS true
#define ENABLE_TURBIDITY true
#define ENABLE_FLAME true
#define ENABLE_VIBRATION true
#define ENABLE_ULTRASONIC true
#define ENABLE_GPS true
#define ENABLE_BATTERY false
// Values remain raw until calibration is explicitly enabled. No guessed units.
#define SOIL_CALIBRATED false
#define SOIL_ADC_1 3600.0f
#define SOIL_VWC_1_PCT 0.0f
#define SOIL_ADC_2 1800.0f
#define SOIL_VWC_2_PCT 45.0f
#define PH_CALIBRATED false
#define PH_MV_1 2500.0f
#define PH_VALUE_1 7.0f
#define PH_MV_2 3000.0f
#define PH_VALUE_2 4.0f
#define TDS_CALIBRATED false
#define TDS_PPM_PER_MV 1.0f
#define TDS_OFFSET_PPM 0.0f
#define TURBIDITY_CALIBRATED false
#define TURBIDITY_NTU_PER_MV -1.0f
#define TURBIDITY_OFFSET_NTU 3300.0f
#define WATER_HEIGHT_CALIBRATED false
#define WATER_REFERENCE_CM 300.0f
// S3 GPIO0 is NOT an ADC pin. Battery is disabled until wired to this ADC pin.
#define S3_BATTERY_PIN -1
// The SW420 module needs a measured debounce interval for your installation.
#define VIBRATION_DEBOUNCE_US 10000
