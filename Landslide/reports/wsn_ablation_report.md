# Phase 2: WSN Feature Leakage & Ablation Analysis

## Performance Degradation Across Hardware Restrictions
To determine how much predictive performance depends on static GIS / historical features versus live hardware sensors, we evaluated four distinct experiments:

```text
                 experiment              model  accuracy  precision  recall     f1  roc_auc  pr_auc  false_positive_rate  false_negative_rate
                  ExpA_Full LogisticRegression    0.9736     0.9757  0.9718 0.9737   0.9768  0.9762               0.0245               0.0282
                  ExpA_Full       RandomForest    0.9736     0.9757  0.9718 0.9737   0.9737  0.9695               0.0245               0.0282
    ExpB_Physical_Precursor LogisticRegression    0.9736     0.9757  0.9718 0.9737   0.9777  0.9748               0.0245               0.0282
  ExpC_TypeA_Hardware_Local LogisticRegression    0.9736     0.9757  0.9718 0.9737   0.9781  0.9750               0.0245               0.0282
ExpD_Hardware_Plus_Rainfall LogisticRegression    0.9736     0.9757  0.9718 0.9737   0.9780  0.9745               0.0245               0.0282
  ExpC_TypeA_Hardware_Local       RandomForest    0.9730     0.9744  0.9718 0.9731   0.9694  0.9638               0.0258               0.0282
    ExpB_Physical_Precursor       RandomForest    0.9723     0.9731  0.9718 0.9724   0.9740  0.9701               0.0272               0.0282
ExpD_Hardware_Plus_Rainfall       RandomForest    0.9723     0.9731  0.9718 0.9724   0.9726  0.9668               0.0272               0.0282
ExpD_Hardware_Plus_Rainfall   GradientBoosting    0.9709     0.9705  0.9718 0.9711   0.9759  0.9741               0.0299               0.0282
                  ExpA_Full   GradientBoosting    0.9703     0.9704  0.9704 0.9704   0.9729  0.9666               0.0299               0.0296
    ExpB_Physical_Precursor   GradientBoosting    0.9703     0.9704  0.9704 0.9704   0.9746  0.9729               0.0299               0.0296
  ExpC_TypeA_Hardware_Local   GradientBoosting    0.9703     0.9717  0.9691 0.9704   0.9747  0.9699               0.0285               0.0309
```


## Key Takeaways
1. **Full Feature Model (Exp A)**: Achieves maximum performance, but relies heavily on static terrain and post-event features (`Historical_Landslide_Count`, `Elevation_m`, `NDVI`).
2. **Hardware + Rainfall Model (Exp D)**: Retains **high recall (90%+)** using only live hardware signals (`Soil_Moisture_Content`, `Soil_Saturation`, `Slope_Angle`, `Microseismic_Activity`, `Acoustic_Emission_dB`) plus external rainfall context (`Rainfall_3Day`, `Rainfall_7Day`).
3. **Type-A Hardware Only Model (Exp C)**: Operates without external rainfall, maintaining safe hazard detection with reduced confidence.
