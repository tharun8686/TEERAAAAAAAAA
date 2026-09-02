# Episode-Level Chronological Data Splitting Report

- **Total Dataset Size:** `62,630` samples
- **Training Split (Episode 1):** `24,994` samples (Index `0` to `24993`)
  └─ Fire Alarm Balance: `{1: 21816, 0: 3178}`
- **Validation Split (Episode 2 - Early):** `18,818` samples (Index `24994` to `43811`)
  └─ Fire Alarm Balance: `{1: 15640, 0: 3178}`
- **Test Split (Episode 2 - Late & Recovery):** `18,818` samples (Index `43812` to `62629`)
  └─ Fire Alarm Balance: `{0: 11517, 1: 7301}`

*Episode-level chronological splitting ensures realistic time-ordering without data leakage between episodes.*
