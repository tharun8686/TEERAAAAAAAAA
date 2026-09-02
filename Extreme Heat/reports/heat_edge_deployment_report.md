# Edge AI Deployment Preparation

This report summarizes the model's footprint and parameters for deployment on a microcontroller (e.g., ESP32).

## Model Architecture
- **Base Estimator:** LogisticRegression
- **Number of Features:** 14
- **Target Classes:** {"0": "NORMAL", "1": "WATCH", "2": "WARNING", "3": "CRITICAL"}

## Standard Scaler Parameters (C-Array Format)
```c
const float scaler_means[14] = {24.4199, 80.0019, 183.8032, 1.1556, 2.3798, -0.0027, 0.0064, -0.1338, 24.4250, 80.0360, 3.8101, 15.5455, 0.8799, 0.0000};
const float scaler_scales[14] = {5.0296, 20.4823, 253.2538, 2.5414, 1.2490, 1.6184, 6.4406, 117.1707, 2.6302, 11.1980, 2.1509, 8.0068, 3.0558, 1.0000};
```

## Logistic Regression Weights (C-Array Format)
const int num_classes = 3;

// Class 0 Weights
```c
const float class_0_weights[14] = {-11.4252, -4.1400, -0.4111, 0.0346, 0.0907, -0.4327, -0.9614, 0.0193, -3.4685, -2.9972, -1.2988, 1.2680, -0.2544, 0.0000};
const float class_0_intercept = 16.0289;
```

// Class 1 Weights
```c
const float class_1_weights[14] = {-2.4430, -2.2509, 0.5308, 0.1343, -0.0997, -0.8558, -1.0103, -0.0478, 0.6236, 0.4865, 0.3185, 0.4379, -0.0139, 0.0000};
const float class_1_intercept = 3.2168;
```

// Class 2 Weights
```c
const float class_2_weights[14] = {13.8682, 6.3909, -0.1197, -0.1689, 0.0090, 1.2886, 1.9718, 0.0285, 2.8449, 2.5107, 0.9803, -1.7059, 0.2683, 0.0000};
const float class_2_intercept = -19.2457;
```

## Edge Inference Strategy
1. Collect features from sensors.
2. Scale features: `(x - mean) / scale`.
3. Compute dot product for each class: `sum(scaled_x * weights) + intercept`.
4. Apply softmax to get probabilities.
