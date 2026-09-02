# Industrial Emissions Edge AI Deployment Prep

This report compiles model coefficients and scaling configurations for ESP32 microcontroller deployment.

## Model Footprint
- **Base Estimator:** LogisticRegression
- **Number of Features:** 17
## StandardScaler Parameters
```c
const float scaler_means[17] = {418.3909, 697.5341, 25.0000, 45.0000, 28.0000, 65.0000, 1012.0000, 0.0017, 0.0000, 0.0000, 418.3720, 25.0000, 7.4426, 0.0000, 1.0003, 1.0000, 10.1228};
const float scaler_scales[17] = {83.9583, 87.5153, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 7.4473, 1.0000, 1.0000, 83.1704, 1.0000, 9.3790, 1.0000, 0.0339, 1.0000, 4.2652};
```

## Logistic Regression Weights (Class-wise C-arrays)
const int num_classes = 3;

// Class 0 Weights
```c
const float class_0_weights[17] = {-4.8338, -0.8049, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.1468, 0.0000, 0.0000, -4.8729, 0.0000, -1.3273, 0.0000, -2.2777, 0.0000, -1.5612};
const float class_0_intercept = 0.0947;
```

// Class 1 Weights
```c
const float class_1_weights[17] = {-2.8717, -0.3046, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, -0.0723, 0.0000, 0.0000, -2.1197, 0.0000, 0.6237, 0.0000, 0.2751, 0.0000, 1.4333};
const float class_1_intercept = 9.4532;
```

// Class 2 Weights
```c
const float class_2_weights[17] = {7.7055, 1.1095, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, -0.0745, 0.0000, 0.0000, 6.9926, 0.0000, 0.7036, 0.0000, 2.0026, 0.0000, 0.1279};
const float class_2_intercept = -9.5479;
```

## Embedded Execution Strategy
1. Sample sensors (MQ gas, PM2.5, PM10, DHT22 Temp/Humid, BMP280 pressure).
2. Compute rolling stats and rate features sequentially.
3. Scale inputs using `scaler_means` and `scaler_scales`.
4. Perform matrix dot product for each class probability.
