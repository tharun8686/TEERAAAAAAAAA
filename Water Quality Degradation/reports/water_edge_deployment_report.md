# Water Quality Edge AI Deployment Prep

This report compiles model coefficients, scaling configurations, and imputation constants for ESP32 microcontroller deployment.

## Model Footprint
- **Base Estimator:** LogisticRegression
- **Number of Features:** 26
## Imputer Fill Constants (C-Array Format)
```c
const float imputer_means[26] = {8.0561, 7.4729, 217755.2930, 358.3291, 6.1098, 26.3939, -0.0006, -0.0031, -111.5208, -0.4381, -0.0010, 8.0599, 8.6776, 218200.7949, 321.9803, 6.1852, 0.3852, 0.2094, 101035.4783, 12.9196, 0.2035, 1.0612, 1.2509, 1.0197, 1.8951, 1.7703};
```

## StandardScaler Parameters
```c
const float scaler_means[26] = {8.0561, 7.4729, 217755.2930, 358.3291, 6.1098, 26.3939, -0.0006, -0.0031, -111.5208, -0.4381, -0.0010, 8.0599, 8.6776, 218200.7949, 321.9803, 6.1852, 0.3852, 0.2094, 101035.4783, 12.9196, 0.2035, 1.0612, 1.2509, 1.0197, 1.8951, 1.7703};
const float scaler_scales[26] = {0.4551, 1.7448, 343244.7911, 45.6970, 0.4566, 1.5809, 0.5625, 0.8405, 241313.8756, 51.7919, 0.4168, 0.2440, 4.2609, 299631.9243, 39.8019, 0.4247, 0.1329, 2.4891, 143999.7920, 44.7090, 0.3910, 0.4433, 0.1043, 0.8263, 0.4371, 1.7404};
```

## Logistic Regression Weights (Class-wise C-arrays)
const int num_classes = 4;

// Class 0 Weights
```c
const float class_0_weights[26] = {0.3574, -2.1846, 0.5567, -1.1855, -0.2882, -0.5854, -0.3074, 0.1167, 0.7392, -0.3485, 0.6399, -0.4524, 0.3335, -1.7294, 0.6226, 0.1995, 0.5531, -0.5263, 1.5018, -2.0429, -1.3231, -4.5729, -0.1728, -0.5249, -1.2301, -1.5697};
const float class_0_intercept = 13.6242;
```

// Class 1 Weights
```c
const float class_1_weights[26] = {-1.1888, -1.8931, 1.2397, -1.0157, 1.1270, -0.5638, -0.1645, 0.0044, 0.5152, 0.0118, 0.3466, -1.6343, 0.3053, -0.8171, 0.4111, -0.2977, 0.3984, -0.5600, 1.0430, -1.2584, -0.8883, -0.4367, -0.0817, -0.4389, 0.7039, -0.3300};
const float class_1_intercept = 12.2049;
```

// Class 2 Weights
```c
const float class_2_weights[26] = {-1.9016, 1.2326, 0.5474, -0.0067, -0.5132, -0.0363, 0.0130, -0.1017, 0.3716, -0.0277, 0.0506, -2.4013, -1.5085, -0.0101, 0.0410, -0.4861, 0.9337, 0.5233, 1.0707, -0.2884, -0.6100, 2.1826, -0.3663, -0.1811, 0.1932, 0.1293};
const float class_2_intercept = 5.9661;
```

// Class 3 Weights
```c
const float class_3_weights[26] = {2.7330, 2.8450, -2.3438, 2.2079, -0.3255, 1.1856, 0.4588, -0.0194, -1.6260, 0.3643, -1.0371, 4.4880, 0.8698, 2.5566, -1.0747, 0.5842, -1.8853, 0.5630, -3.6155, 3.5897, 2.8214, 2.8270, 0.6208, 1.1449, 0.3330, 1.7704};
const float class_3_intercept = -31.7952;
```

## Embedded Execution Strategy
1. Sample sensors (pH, turbidity, EC, TDS, DHT22 temp).
2. Compute rolling stats and rate features sequentially.
3. Replace NaNs with `imputer_means`.
4. Scale inputs using `scaler_means` and `scaler_scales`.
5. Perform matrix dot product for each class probability.
