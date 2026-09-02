// ============================================================
// model_rf.h  --  Landslide Edge-AI Random Forest Inference
// AUTO-GENERATED -- DO NOT EDIT MANUALLY
// Model: CalibratedClassifierCV (RandomForest, 50 estimators x 3 folds)
// Features: 8, Classes: 2 (NORMAL=0, INSTABILITY=1)
// Scaler: StandardScaler (exact params from landslide_model_config.json)
// Calibration: Sigmoid Platt scaling, 3-fold CV
// ============================================================
#pragma once
#include <math.h>

// --- Feature Index Constants ---
// ['soil_moisture_vwc', 'soil_moisture_rate', 'tilt_magnitude', 'tilt_rate', 'vibration_rate', 'temperature', 'humidity', 'rainfall_24h']
#define F_SOIL_MOISTURE_VWC   0
#define F_SOIL_MOISTURE_RATE  1
#define F_TILT_MAGNITUDE      2
#define F_TILT_RATE           3
#define F_VIBRATION_RATE      4
#define F_TEMPERATURE         5
#define F_HUMIDITY            6
#define F_RAINFALL_24H        7

// --- Exact StandardScaler Parameters (8 features) ---
static const float RF_SCALER_MEAN[8] = {
    0.2425563437f, -0.0000001706f, 2.6065731255f, -0.0002950414f, 1.8603058954f, 22.5080295793f, 64.3494923505f, 3.2525382473f
};
static const float RF_SCALER_STD[8] = {
    0.1453090278f, 0.0020670520f, 0.3755277481f, 0.3969273899f, 2.5857768665f, 3.5420244966f, 2.0181190591f, 10.0905952957f
};

// --- Sigmoid Platt Calibration Parameters (per CV fold) ---
// P_cal = 1 / (1 + exp(a * raw_prob + b))
static const float RF_SIGMOID_A[3] = {
    -21.5204512000f, -21.4991456400f, -21.5364626800f
};
static const float RF_SIGMOID_B[3] = {
    11.9519307600f, 11.9398569800f, 11.9499463700f
};

// --- StandardScaler normalization ---
inline void rf_scale_features(const float* raw, float* scaled) {
    for (int i = 0; i < 8; i++) {
        scaled[i] = (raw[i] - RF_SCALER_MEAN[i]) / RF_SCALER_STD[i];
    }
}

// --- Sigmoid calibration ---
inline float rf_sigmoid(float x, float a, float b) {
    return 1.0f / (1.0f + expf(a * x + b));
}

// ============================================================
// DECISION TREE FUNCTIONS  (150 trees)
// Each returns raw P(class=1) from leaf vote fractions.
// ============================================================
static float rf_tree_000(const float* x) {
  if (x[6] <= 0.24832809f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[5] <= 0.72283569f) {
        if (x[1] <= -0.47015239f) {
          if (x[1] <= -0.94038731f) {
            if (x[4] <= 2.56777543f) {
              if (x[1] <= -1.19727486f) {
                if (x[7] <= -0.31327173f) {
                  if (x[0] <= 0.96875370f) {
                    if (x[5] <= -0.23735271f) {
                      return 0.00000000f;
                    } else {
                      return 0.00656455f;
                    }
                  } else {
                    if (x[0] <= 0.98268953f) {
                      return 0.72727273f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                return 0.00000000f;
              }
            } else {
              return 0.99774266f;
            }
          } else {
            if (x[0] <= -0.66947901f) {
              if (x[5] <= -0.53777590f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[6] <= 0.26997598f) {
            return 0.00000000f;
          } else {
            if (x[0] <= -0.68496326f) {
              if (x[0] <= -0.72831911f) {
                if (x[4] <= 2.56777543f) {
                  if (x[7] <= -0.31327173f) {
                    if (x[0] <= -0.73141596f) {
                      return 0.00000000f;
                    } else {
                      return 0.00148699f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[0] <= -0.70979998f) {
                  if (x[5] <= -0.37580223f) {
                    if (x[6] <= 0.30974765f) {
                      return 0.00000000f;
                    } else {
                      return 0.00698856f;
                    }
                  } else {
                    if (x[1] <= 0.32663454f) {
                      return 0.57253731f;
                    } else {
                      return 0.27139875f;
                    }
                  }
                } else {
                  if (x[1] <= 0.32663454f) {
                    if (x[5] <= 0.60157505f) {
                      return 0.12772377f;
                    } else {
                      return 0.51086957f;
                    }
                  } else {
                    if (x[4] <= 2.56777543f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            } else {
              if (x[1] <= 0.47031744f) {
                if (x[5] <= 0.49748375f) {
                  if (x[4] <= 2.56777543f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[5] <= -0.19949658f) {
                      return 0.99750212f;
                    } else {
                      return 0.99912038f;
                    }
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[4] <= 2.56777543f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[5] <= -1.41188180f) {
                    return 0.97142857f;
                  } else {
                    if (x[3] <= -1.51086811f) {
                      return 0.80769231f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            }
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_001(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_002(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_003(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_004(const float* x) {
  if (x[7] <= -0.24832809f) {
    if (x[3] <= 1.51235481f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_005(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[0] <= -0.67839792f) {
      if (x[0] <= -0.69115695f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[3] <= 1.51235481f) {
          if (x[4] <= 2.56777543f) {
            if (x[6] <= -4.53585362f) {
              if (x[7] <= 6.52443767f) {
                return 0.55555556f;
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[4] <= 0.63412052f) {
                if (x[5] <= -0.61165369f) {
                  return 0.00000000f;
                } else {
                  if (x[7] <= -0.15871593f) {
                    return 0.01140065f;
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                return 0.00000000f;
              }
            }
          } else {
            return 1.00000000f;
          }
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[0] <= -0.68496326f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[0] <= -0.68186641f) {
          if (x[4] <= 2.56777543f) {
            if (x[6] <= -2.69830084f) {
              return 0.78571429f;
            } else {
              if (x[5] <= -0.72605887f) {
                if (x[5] <= -0.74656585f) {
                  if (x[7] <= 0.16851947f) {
                    return 0.00000000f;
                  } else {
                    if (x[7] <= 0.69713050f) {
                      return 0.62500000f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  return 0.72727273f;
                }
              } else {
                if (x[7] <= -0.30974765f) {
                  if (x[1] <= 0.10893319f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= 0.32663454f) {
                      return 0.29787234f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[1] <= 0.47031744f) {
            if (x[1] <= 0.30244550f) {
              if (x[4] <= 2.56777543f) {
                if (x[4] <= 0.63412052f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[0] <= 1.44566834f) {
                    if (x[1] <= -0.10876816f) {
                      return 0.01431801f;
                    } else {
                      return 0.00169348f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[5] <= -1.40424925f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[7] <= 1.17590106f) {
                  if (x[4] <= 2.56777543f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[0] <= -0.64780107f) {
                      return 0.99553970f;
                    } else {
                      return 0.99873217f;
                    }
                  }
                } else {
                  if (x[4] <= 2.56777543f) {
                    if (x[0] <= 1.37134391f) {
                      return 0.00000000f;
                    } else {
                      return 0.17500000f;
                    }
                  } else {
                    if (x[4] <= 4.50143015f) {
                      return 0.99322034f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            }
          } else {
            if (x[6] <= -0.85823098f) {
              if (x[0] <= -0.52547559f) {
                if (x[3] <= -1.51086811f) {
                  return 0.50000000f;
                } else {
                  if (x[4] <= 1.60094798f) {
                    if (x[6] <= -1.27608544f) {
                      return 0.00000000f;
                    } else {
                      return 0.03153153f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[0] <= -0.56263772f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[4] <= 2.56777543f) {
                  if (x[5] <= -1.19063491f) {
                    if (x[0] <= 0.38654624f) {
                      return 0.08755760f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    if (x[7] <= 0.75351566f) {
                      return 0.00478951f;
                    } else {
                      return 0.18181818f;
                    }
                  }
                } else {
                  if (x[3] <= -1.51086811f) {
                    return 0.87500000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            }
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_006(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_007(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[1] <= -0.47015239f) {
      if (x[0] <= -0.67839792f) {
        if (x[4] <= 2.56777543f) {
          if (x[1] <= -0.94038731f) {
            return 0.00000000f;
          } else {
            if (x[7] <= 4.53585362f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[7] <= 5.25325418f) {
                return 0.55555556f;
              } else {
                return 0.00000000f;
              }
            }
          }
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_008(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[5] <= -1.34061968f) {
      if (x[3] <= -1.51086811f) {
        if (x[0] <= 1.74915946f) {
          if (x[7] <= -0.03285616f) {
            if (x[4] <= 4.50143015f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[4] <= 2.56777543f) {
              return 0.00000000f;
            } else {
              return 0.88888889f;
            }
          }
        } else {
          if (x[6] <= -0.29437923f) {
            if (x[7] <= 0.36989510f) {
              return 0.80952381f;
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[0] <= -0.63231683f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[5] <= 1.40932536f) {
          if (x[3] <= -1.51086811f) {
            if (x[5] <= 0.20395488f) {
              if (x[7] <= 1.90538430f) {
                if (x[1] <= -0.32646950f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[4] <= 4.50143015f) {
                    if (x[0] <= 1.45805573f) {
                      return 0.00000000f;
                    } else {
                      return 0.03324468f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[3] <= -4.53409100f) {
                  return 0.00000000f;
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[4] <= 2.56777543f) {
            if (x[1] <= 0.10893319f) {
              if (x[1] <= -0.10876816f) {
                return 0.62500000f;
              } else {
                return 0.75000000f;
              }
            } else {
              if (x[5] <= 1.40933549f) {
                return 0.72727273f;
              } else {
                return 0.94117647f;
              }
            }
          } else {
            return 1.00000000f;
          }
        }
      }
    }
  }
}

static float rf_tree_009(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[1] <= -3.80969107f) {
      if (x[3] <= -1.51086811f) {
        if (x[1] <= -4.89819789f) {
          return 0.81250000f;
        } else {
          return 0.00000000f;
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[3] <= -1.51086811f) {
        if (x[7] <= -0.05802812f) {
          if (x[3] <= -7.55731416f) {
            if (x[3] <= -13.60376024f) {
              return 0.80000000f;
            } else {
              if (x[4] <= 10.30239487f) {
                return 0.85714286f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[4] <= 4.50143015f) {
              if (x[4] <= 2.56777543f) {
                if (x[0] <= 1.45805573f) {
                  if (x[6] <= 0.30974765f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= -0.59746993f) {
                      return 0.00218978f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  if (x[5] <= -0.83672637f) {
                    if (x[0] <= 1.47044313f) {
                      return 0.55555556f;
                    } else {
                      return 0.02631579f;
                    }
                  } else {
                    if (x[0] <= 1.76584804f) {
                      return 0.00000000f;
                    } else {
                      return 0.01109570f;
                    }
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[1] <= 1.19743997f) {
            if (x[4] <= 4.50143015f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[4] <= 6.43508506f) {
                if (x[7] <= -0.03285616f) {
                  return 0.88235294f;
                } else {
                  if (x[7] <= 0.69713050f) {
                    return 1.00000000f;
                  } else {
                    if (x[6] <= -0.79781833f) {
                      return 0.99819495f;
                    } else {
                      return 0.94444444f;
                    }
                  }
                }
              } else {
                if (x[3] <= -10.58053732f) {
                  return 0.54545455f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[1] <= 2.93905079f) {
              if (x[6] <= -1.94314229f) {
                return 0.89473684f;
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[4] <= 3.53460270f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_010(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_011(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[0] <= -0.68496326f) {
        if (x[1] <= 0.32663454f) {
          if (x[4] <= 2.56777543f) {
            if (x[7] <= -0.31327173f) {
              if (x[1] <= -0.10876816f) {
                if (x[5] <= 0.92952350f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[4] <= 0.63412052f) {
                  if (x[5] <= -0.31340708f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= 0.10893319f) {
                      return 0.00801813f;
                    } else {
                      return 0.02985075f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              if (x[5] <= 0.69923663f) {
                return 0.00000000f;
              } else {
                if (x[5] <= 0.74887705f) {
                  return 0.69230769f;
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            if (x[7] <= -0.30974765f) {
              if (x[4] <= 4.50143015f) {
                if (x[5] <= 0.95334992f) {
                  return 1.00000000f;
                } else {
                  if (x[1] <= 0.10893319f) {
                    return 1.00000000f;
                  } else {
                    if (x[5] <= 1.06301397f) {
                      return 0.95652174f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                return 1.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[0] <= -0.68186641f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[1] <= 0.30244550f) {
            if (x[3] <= -1.51086811f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[7] <= 0.85823098f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_012(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_013(const float* x) {
  if (x[0] <= -0.68496326f) {
    if (x[0] <= -0.72162992f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[5] <= 1.20154476f) {
        if (x[0] <= -0.71648917f) {
          if (x[5] <= -0.53051892f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[1] <= 0.32663454f) {
            if (x[1] <= -0.32646950f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[4] <= 0.63412052f) {
                if (x[1] <= -0.10876816f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[6] <= 0.31327173f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= 0.10893319f) {
                      return 0.01393867f;
                    } else {
                      return 0.04897959f;
                    }
                  }
                }
              } else {
                if (x[3] <= -1.51086811f) {
                  if (x[0] <= -0.68806010f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[1] <= -0.10876816f) {
                      return 0.62857143f;
                    } else {
                      return 0.14285714f;
                    }
                  }
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[5] <= 0.37749580f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[1] <= 0.47031744f) {
                if (x[4] <= 0.63412052f) {
                  return 0.00000000f;
                } else {
                  if (x[3] <= -1.51086811f) {
                    if (x[5] <= 0.65717927f) {
                      return 0.28571429f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[3] <= 1.51235481f) {
                  if (x[5] <= 0.38384403f) {
                    if (x[1] <= 0.76203725f) {
                      return 0.72727273f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  } else {
    if (x[4] <= 0.63412052f) {
      if (x[1] <= -0.47015239f) {
        if (x[7] <= -0.30068575f) {
          if (x[1] <= -0.94038731f) {
            if (x[6] <= 0.31327173f) {
              return 0.00000000f;
            } else {
              if (x[5] <= -0.23713300f) {
                if (x[5] <= -0.23964551f) {
                  if (x[1] <= -1.63267761f) {
                    if (x[5] <= -0.77276057f) {
                      return 0.00000000f;
                    } else {
                      return 0.02358491f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 0.60000000f;
                }
              } else {
                return 0.00000000f;
              }
            }
          } else {
            if (x[6] <= 0.31381084f) {
              return 0.00000000f;
            } else {
              if (x[0] <= 1.31869757f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[0] <= 1.32798809f) {
                  return 0.69230769f;
                } else {
                  return 0.01843318f;
                }
              }
            }
          }
        } else {
          if (x[6] <= 0.29162385f) {
            if (x[0] <= -0.66811639f) {
              if (x[6] <= 0.15871593f) {
                return 0.00000000f;
              } else {
                if (x[1] <= -0.76187220f) {
                  return 0.00000000f;
                } else {
                  if (x[7] <= -0.23423179f) {
                    return 0.00000000f;
                  } else {
                    if (x[7] <= -0.20905984f) {
                      return 0.60000000f;
                    } else {
                      return 0.51515152f;
                    }
                  }
                }
              }
            } else {
              if (x[1] <= -1.41062218f) {
                return 0.00000000f;
              } else {
                if (x[0] <= -0.35514891f) {
                  return 0.00000000f;
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            }
          } else {
            if (x[5] <= -1.25364119f) {
              if (x[0] <= -0.65399477f) {
                if (x[0] <= -0.67257586f) {
                  return 0.00000000f;
                } else {
                  return 0.84000000f;
                }
              } else {
                if (x[0] <= 1.37444079f) {
                  return 0.00000000f;
                } else {
                  return 0.72727273f;
                }
              }
            } else {
              return 0.00000000f;
            }
          }
        }
      } else {
        if (x[6] <= -1.15425318f) {
          if (x[6] <= -1.32038808f) {
            if (x[6] <= -4.08225489f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[1] <= 4.24525881f) {
                if (x[6] <= -2.75367916f) {
                  if (x[7] <= 3.07134914f) {
                    if (x[7] <= 2.90169024f) {
                      return 0.01838235f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  if (x[0] <= -0.27617930f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[5] <= -0.85067672f) {
                      return 0.15068493f;
                    } else {
                      return 0.05394990f;
                    }
                  }
                }
              } else {
                if (x[5] <= -0.18345812f) {
                  return 0.00000000f;
                } else {
                  if (x[1] <= 5.76916838f) {
                    return 0.78947368f;
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_014(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[3] <= -7.55731416f) {
      if (x[6] <= -1.55297691f) {
        return 0.00000000f;
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_015(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_016(const float* x) {
  if (x[0] <= -0.68496326f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_017(const float* x) {
  if (x[6] <= 0.24832809f) {
    if (x[1] <= -0.84653383f) {
      if (x[3] <= 1.51235481f) {
        if (x[4] <= 2.56777543f) {
          if (x[5] <= 1.36813807f) {
            if (x[0] <= 1.68722248f) {
              if (x[7] <= 4.62395525f) {
                return 0.00000000f;
              } else {
                if (x[5] <= -0.26730931f) {
                  if (x[7] <= 4.80015898f) {
                    return 0.50000000f;
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              if (x[1] <= -0.97957355f) {
                return 0.00000000f;
              } else {
                if (x[0] <= 1.69806141f) {
                  return 0.41666667f;
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            if (x[6] <= -0.04265970f) {
              if (x[5] <= 1.38084733f) {
                if (x[6] <= -0.55868477f) {
                  return 0.00000000f;
                } else {
                  return 0.33333333f;
                }
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[0] <= 0.49803276f) {
                if (x[1] <= -0.94038731f) {
                  return 0.00000000f;
                } else {
                  return 0.40000000f;
                }
              } else {
                return 0.63636364f;
              }
            }
          }
        } else {
          if (x[3] <= -1.51086811f) {
            if (x[0] <= 1.03998119f) {
              return 0.96296296f;
            } else {
              return 0.87500000f;
            }
          } else {
            return 1.00000000f;
          }
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_018(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_019(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_020(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_021(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[7] <= -0.24832809f) {
      if (x[0] <= -0.67839792f) {
        if (x[4] <= 2.56777543f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[3] <= -4.53409100f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[0] <= -0.67325717f) {
          if (x[4] <= 2.56777543f) {
            if (x[7] <= -0.30068575f) {
              if (x[0] <= -0.67567271f) {
                if (x[1] <= 0.10893319f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[5] <= -0.27301824f) {
                  if (x[3] <= -1.51086811f) {
                    return 0.00000000f;
                  } else {
                    return 0.16666667f;
                  }
                } else {
                  if (x[1] <= 0.10893319f) {
                    if (x[5] <= 1.40680152f) {
                      return 0.00000000f;
                    } else {
                      return 0.26086957f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            } else {
              if (x[0] <= -0.67567271f) {
                return 0.37500000f;
              } else {
                return 0.00000000f;
              }
            }
          } else {
            if (x[3] <= -1.51086811f) {
              if (x[5] <= 1.40668702f) {
                return 1.00000000f;
              } else {
                return 0.92000000f;
              }
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[5] <= -0.86181006f) {
        if (x[4] <= 2.56777543f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[7] <= 8.65146828f) {
            if (x[0] <= 1.72128779f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[6] <= -0.94885004f) {
                if (x[3] <= -4.53409100f) {
                  if (x[6] <= -1.43970317f) {
                    return 0.00000000f;
                  } else {
                    return 0.53846154f;
                  }
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[7] <= 0.11817556f) {
                  if (x[5] <= -1.06970882f) {
                    if (x[6] <= 0.03285616f) {
                      return 0.99065421f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[7] <= 0.01748774f) {
                      return 1.00000000f;
                    } else {
                      return 0.90000000f;
                    }
                  }
                } else {
                  if (x[5] <= -1.40864432f) {
                    return 0.97560976f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            }
          } else {
            if (x[1] <= 0.10893319f) {
              return 0.97674419f;
            } else {
              return 0.89473684f;
            }
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_022(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_023(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[7] <= -0.24832809f) {
      if (x[1] <= -0.47015239f) {
        if (x[7] <= -0.29162385f) {
          if (x[3] <= -1.51086811f) {
            if (x[4] <= 4.50143015f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[4] <= 1.60094798f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[5] <= 1.27625757f) {
            if (x[7] <= -0.26997598f) {
              if (x[0] <= 1.68257719f) {
                if (x[0] <= -0.66173688f) {
                  return 0.04545455f;
                } else {
                  return 0.00000000f;
                }
              } else {
                return 0.57142857f;
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[0] <= -0.67722112f) {
              return 0.00000000f;
            } else {
              return 0.66666667f;
            }
          }
        }
      } else {
        if (x[6] <= 0.26997598f) {
          return 0.00000000f;
        } else {
          if (x[3] <= -7.55731416f) {
            if (x[1] <= -0.10876816f) {
              return 0.91304348f;
            } else {
              return 0.97500000f;
            }
          } else {
            if (x[1] <= 0.47031744f) {
              if (x[1] <= 0.30244550f) {
                if (x[0] <= -0.69115695f) {
                  if (x[5] <= 0.20868590f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[5] <= 0.95825484f) {
                      return 0.35517044f;
                    } else {
                      return 0.01210491f;
                    }
                  }
                } else {
                  if (x[4] <= 2.56777543f) {
                    if (x[5] <= 1.19242108f) {
                      return 0.04707313f;
                    } else {
                      return 0.02694689f;
                    }
                  } else {
                    if (x[3] <= -4.53409100f) {
                      return 0.37583893f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                if (x[3] <= -1.51086811f) {
                  if (x[4] <= 4.50143015f) {
                    if (x[6] <= 0.30974765f) {
                      return 0.00000000f;
                    } else {
                      return 0.02222222f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            } else {
              if (x[4] <= 2.56777543f) {
                if (x[0] <= 1.76464367f) {
                  if (x[6] <= 0.31327173f) {
                    return 0.00000000f;
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  if (x[5] <= -0.78988197f) {
                    return 0.66666667f;
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[0] <= -0.67876956f) {
                  return 0.98507463f;
                } else {
                  if (x[0] <= -0.64160737f) {
                    return 1.00000000f;
                  } else {
                    if (x[3] <= -1.51086811f) {
                      return 0.89743590f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            }
          }
        }
      }
    } else {
      if (x[6] <= -4.02989721f) {
        if (x[5] <= -0.39088777f) {
          if (x[0] <= 1.76619208f) {
            if (x[0] <= 1.00436744f) {
              if (x[4] <= 2.56777543f) {
                return 0.02247191f;
              } else {
                return 0.87500000f;
              }
            } else {
              if (x[3] <= -1.51086811f) {
                if (x[4] <= 4.50143015f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[6] <= -9.67093229f) {
                  return 0.50000000f;
                } else {
                  if (x[6] <= -7.83337951f) {
                    if (x[7] <= 8.22354460f) {
                      return 0.96153846f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[4] <= 1.60094798f) {
                      return 0.63076923f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            }
          } else {
            if (x[1] <= 0.41129617f) {
              if (x[6] <= -7.34957457f) {
                if (x[5] <= -1.20693702f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[4] <= 2.56777543f) {
                  if (x[7] <= 4.69947124f) {
                    if (x[6] <= -4.64912724f) {
                      return 0.40000000f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 0.96551724f;
                }
              }
            } else {
              return 0.58333333f;
            }
          }
        } else {
          if (x[0] <= -0.70001394f) {
            return 0.00000000f;
          } else {
            if (x[6] <= -15.48565340f) {
              if (x[0] <= 0.18370267f) {
                return 0.93103448f;
              } else {
                if (x[5] <= 1.29101562f) {
                  return 0.60000000f;
                } else {
                  return 0.90909091f;
                }
              }
            } else {
              if (x[6] <= -9.48214245f) {
                return 0.00000000f;
              } else {
                if (x[4] <= 2.56777543f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[3] <= -4.53409100f) {
                    return 0.66666667f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            }
          }
        }
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[1] <= 0.30244550f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[1] <= 1.63284260f) {
              if (x[6] <= -0.74747440f) {
                if (x[4] <= 0.63412052f) {
                  if (x[0] <= 1.37134391f) {
                    if (x[6] <= -1.32038808f) {
                      return 0.00352734f;
                    } else {
                      return 0.02906977f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[5] <= -1.41385895f) {
                  return 0.36363636f;
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            } else {
              if (x[1] <= 1.85054398f) {
                if (x[0] <= 1.33882701f) {
                  if (x[5] <= 0.39491944f) {
                    return 0.40000000f;
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 0.63636364f;
                }
              } else {
                if (x[1] <= 2.28594661f) {
                  if (x[7] <= 1.02436590f) {
                    return 0.00000000f;
                  } else {
                    if (x[7] <= 1.15022564f) {
                      return 0.53846154f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  if (x[0] <= 0.43454736f) {
                    if (x[1] <= 5.24668503f) {
                      return 0.00000000f;
                    } else {
                      return 0.04081633f;
                    }
                  } else {
                    if (x[3] <= -1.51086811f) {
                      return 0.00000000f;
                    } else {
                      return 0.13664596f;
                    }
                  }
                }
              }
            }
          }
        } else {
          if (x[7] <= 1.22574151f) {
            if (x[5] <= 1.40779555f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[5] <= 1.40799916f) {
                return 0.88461538f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[5] <= -0.99740323f) {
              if (x[4] <= 6.43508506f) {
                if (x[3] <= -4.53409100f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[7] <= 1.25091350f) {
                if (x[0] <= 1.60945719f) {
                  return 1.00000000f;
                } else {
                  return 0.95833333f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        }
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_024(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_025(const float* x) {
  if (x[0] <= -0.67839792f) {
    if (x[0] <= -0.69115695f) {
      if (x[3] <= 1.51235481f) {
        if (x[5] <= -0.37495759f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 0.63412052f) {
        if (x[6] <= -4.17086029f) {
          if (x[0] <= -0.68186641f) {
            if (x[5] <= -0.72043797f) {
              return 0.00000000f;
            } else {
              return 0.76923077f;
            }
          } else {
            if (x[6] <= -5.10222244f) {
              return 0.00000000f;
            } else {
              return 0.46153846f;
            }
          }
        } else {
          if (x[6] <= -0.36989510f) {
            return 0.00000000f;
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[5] <= -0.70386472f) {
          if (x[5] <= -0.70889413f) {
            if (x[3] <= -1.51086811f) {
              if (x[5] <= -0.85105196f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[1] <= 0.10893319f) {
                  return 0.00000000f;
                } else {
                  if (x[7] <= -0.28457570f) {
                    return 0.00000000f;
                  } else {
                    return 0.28571429f;
                  }
                }
              }
            } else {
              return 1.00000000f;
            }
          } else {
            return 0.72000000f;
          }
        } else {
          if (x[5] <= 0.77923170f) {
            if (x[5] <= 0.58855748f) {
              if (x[3] <= -1.51086811f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 1.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[4] <= 2.56777543f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[1] <= -0.32646950f) {
                if (x[5] <= 1.39517456f) {
                  return 1.00000000f;
                } else {
                  return 0.98958333f;
                }
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      }
    }
  } else {
    if (x[4] <= 0.63412052f) {
      if (x[6] <= -1.15425318f) {
        if (x[0] <= 1.22734052f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[6] <= -1.28967828f) {
            if (x[7] <= 8.58249664f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[5] <= -1.23775858f) {
                return 0.82142857f;
              } else {
                if (x[7] <= 9.07536364f) {
                  return 0.33898305f;
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            if (x[1] <= 1.63284260f) {
              if (x[6] <= -1.25896853f) {
                if (x[7] <= 1.26803041f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[7] <= 1.28061634f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= -1.25091708f) {
                      return 0.50000000f;
                    } else {
                      return 0.10416667f;
                    }
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              return 0.62500000f;
            }
          }
        }
      } else {
        if (x[7] <= -0.30068575f) {
          if (x[0] <= -0.65678194f) {
            if (x[0] <= -0.67325717f) {
              if (x[7] <= -0.31327173f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[1] <= 0.32663454f) {
                if (x[1] <= -0.47015239f) {
                  if (x[5] <= -1.31232524f) {
                    return 0.02486188f;
                  } else {
                    if (x[0] <= -0.66328532f) {
                      return 0.00564972f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  if (x[5] <= 0.16280817f) {
                    if (x[5] <= -1.31296682f) {
                      return 0.06174957f;
                    } else {
                      return 0.00458069f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                return 0.00492842f;
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[7] <= -0.29162385f) {
            if (x[5] <= -1.24405551f) {
              if (x[0] <= -0.65089792f) {
                if (x[0] <= -0.66328532f) {
                  if (x[1] <= 0.21778387f) {
                    if (x[5] <= -1.36458302f) {
                      return 0.70000000f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[1] <= -0.10876816f) {
                  if (x[1] <= -0.32646950f) {
                    if (x[1] <= -0.76187220f) {
                      return 0.28571429f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.62500000f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[5] <= -1.41387773f) {
              return 0.68421053f;
            } else {
              if (x[5] <= -1.36553079f) {
                if (x[0] <= -0.65089792f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[5] <= -1.36577243f) {
                    if (x[0] <= 1.65625399f) {
                      return 0.01643489f;
                    } else {
                      return 0.12351544f;
                    }
                  } else {
                    return 0.70000000f;
                  }
                }
              } else {
                if (x[0] <= -0.67325717f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            }
          }
        }
      }
    } else {
      if (x[6] <= -7.79562163f) {
        if (x[3] <= -1.51086811f) {
          if (x[4] <= 2.56777543f) {
            return 0.00000000f;
          } else {
            return 0.87500000f;
          }
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[3] <= -1.51086811f) {
          if (x[3] <= -7.55731416f) {
            if (x[7] <= 0.28179326f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[5] <= -0.91570511f) {
                return 0.00000000f;
              } else {
                return 0.81250000f;
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          return 1.00000000f;
        }
      }
    }
  }
}

static float rf_tree_026(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[3] <= 1.51235481f) {
      if (x[6] <= 0.30068575f) {
        if (x[5] <= 1.25592875f) {
          if (x[0] <= 0.80771759f) {
            if (x[3] <= -1.51086811f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[1] <= -0.76187220f) {
                if (x[6] <= -3.89396870f) {
                  if (x[0] <= -0.28546984f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[5] <= 0.70395544f) {
                  if (x[0] <= -0.69270536f) {
                    if (x[5] <= 0.58062878f) {
                      return 0.00000000f;
                    } else {
                      return 0.46666667f;
                    }
                  } else {
                    if (x[5] <= -1.41232830f) {
                      return 0.75000000f;
                    } else {
                      return 0.23501577f;
                    }
                  }
                } else {
                  return 0.06611570f;
                }
              }
            }
          } else {
            if (x[4] <= 2.56777543f) {
              if (x[6] <= 0.29162385f) {
                if (x[7] <= 1.65970600f) {
                  if (x[4] <= 0.63412052f) {
                    if (x[5] <= -1.38952219f) {
                      return 0.20000000f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[7] <= 1.82936502f) {
                    return 0.69230769f;
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[5] <= -1.27673751f) {
                  return 0.50000000f;
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[5] <= -1.41161305f) {
          if (x[4] <= 2.56777543f) {
            if (x[1] <= -0.76187220f) {
              return 0.00000000f;
            } else {
              if (x[0] <= -0.65554318f) {
                return 0.00000000f;
              } else {
                return 0.11538462f;
              }
            }
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_027(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_028(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[7] <= 0.91058868f) {
      if (x[0] <= -0.67839792f) {
        if (x[0] <= -0.72162992f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[1] <= 0.47031744f) {
          if (x[3] <= -7.55731416f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[0] <= -0.56108931f) {
            if (x[4] <= 2.56777543f) {
              if (x[1] <= 0.76203725f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[5] <= -1.41185319f) {
                if (x[0] <= -0.64470422f) {
                  return 1.00000000f;
                } else {
                  return 0.97619048f;
                }
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[1] <= 0.76203725f) {
              if (x[1] <= 0.62899753f) {
                return 0.00000000f;
              } else {
                if (x[3] <= -1.51086811f) {
                  if (x[5] <= 0.44898553f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= 1.03656754f) {
                      return 0.66666667f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  if (x[5] <= 1.25753385f) {
                    if (x[7] <= 0.74747440f) {
                      return 0.28035601f;
                    } else {
                      return 0.65384615f;
                    }
                  } else {
                    if (x[6] <= 0.14612995f) {
                      return 0.00000000f;
                    } else {
                      return 0.68899522f;
                    }
                  }
                }
              }
            } else {
              if (x[5] <= -1.41343361f) {
                return 0.95000000f;
              } else {
                if (x[1] <= 0.94055232f) {
                  if (x[4] <= 2.56777543f) {
                    if (x[0] <= 1.65006030f) {
                      return 0.00000000f;
                    } else {
                      return 0.09333333f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[1] <= 2.15290689f) {
                    if (x[5] <= -1.11898196f) {
                      return 0.15992293f;
                    } else {
                      return 0.04466119f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            }
          }
        }
      }
    } else {
      if (x[4] <= 2.56777543f) {
        if (x[1] <= -0.47015239f) {
          if (x[0] <= 1.36050493f) {
            if (x[6] <= -4.62395525f) {
              if (x[1] <= -0.94038731f) {
                return 0.00000000f;
              } else {
                return 0.10144928f;
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[4] <= 0.63412052f) {
              if (x[1] <= -0.76187220f) {
                return 0.00000000f;
              } else {
                return 0.23333333f;
              }
            } else {
              return 0.00000000f;
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[7] <= 8.14802885f) {
          if (x[6] <= -1.17539763f) {
            if (x[6] <= -1.27608544f) {
              if (x[1] <= -0.54417084f) {
                if (x[5] <= -0.16041848f) {
                  if (x[7] <= 2.25779164f) {
                    return 1.00000000f;
                  } else {
                    return 0.93750000f;
                  }
                } else {
                  if (x[0] <= 1.16230667f) {
                    return 1.00000000f;
                  } else {
                    if (x[0] <= 1.46115255f) {
                      return 0.93333333f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                if (x[5] <= -1.40068227f) {
                  if (x[1] <= 0.10893319f) {
                    if (x[5] <= -1.40650797f) {
                      return 0.98203593f;
                    } else {
                      return 0.93333333f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            } else {
              if (x[5] <= -1.39823753f) {
                return 0.95652174f;
              } else {
                if (x[0] <= 1.72902989f) {
                  if (x[1] <= 0.10893319f) {
                    if (x[5] <= -0.76496780f) {
                      return 0.99295775f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[6] <= -1.20056957f) {
                    if (x[5] <= 1.06956732f) {
                      return 1.00000000f;
                    } else {
                      return 0.82352941f;
                    }
                  } else {
                    return 0.95876289f;
                  }
                }
              }
            }
          } else {
            if (x[1] <= 0.10893319f) {
              if (x[6] <= -0.94885004f) {
                return 1.00000000f;
              } else {
                if (x[0] <= 1.70236266f) {
                  return 1.00000000f;
                } else {
                  if (x[7] <= 0.92367807f) {
                    return 1.00000000f;
                  } else {
                    return 0.98765432f;
                  }
                }
              }
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[6] <= -8.81508589f) {
            return 1.00000000f;
          } else {
            if (x[0] <= 1.62218863f) {
              return 1.00000000f;
            } else {
              return 0.91666667f;
            }
          }
        }
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_029(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[0] <= -0.68496326f) {
      if (x[0] <= -0.69115695f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[5] <= 1.09020776f) {
          if (x[1] <= -0.10876816f) {
            if (x[6] <= -3.62966311f) {
              return 0.55555556f;
            } else {
              if (x[1] <= -0.32646950f) {
                if (x[5] <= -0.44347103f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= -0.42841890f) {
                    return 0.55555556f;
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[7] <= -0.30974765f) {
                  if (x[5] <= -0.63090092f) {
                    return 0.38095238f;
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            return 0.00000000f;
          }
        } else {
          if (x[0] <= -0.68818396f) {
            if (x[5] <= 1.13396823f) {
              return 0.72727273f;
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[5] <= 1.10581809f) {
              if (x[5] <= 1.10253036f) {
                if (x[1] <= -0.57900307f) {
                  return 0.60000000f;
                } else {
                  return 0.00000000f;
                }
              } else {
                return 0.88235294f;
              }
            } else {
              if (x[0] <= -0.68663555f) {
                return 0.00000000f;
              } else {
                if (x[1] <= 0.10893319f) {
                  if (x[6] <= 0.30974765f) {
                    return 0.00000000f;
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              }
            }
          }
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[3] <= -1.51086811f) {
      if (x[3] <= -7.55731416f) {
        if (x[4] <= 8.36874008f) {
          if (x[4] <= 6.43508506f) {
            return 0.00000000f;
          } else {
            return 0.44444444f;
          }
        } else {
          if (x[5] <= 0.28875320f) {
            return 1.00000000f;
          } else {
            return 0.91666667f;
          }
        }
      } else {
        if (x[4] <= 4.50143015f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          return 1.00000000f;
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_030(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[0] <= -0.67839792f) {
      if (x[7] <= 4.19603205f) {
        if (x[0] <= -0.69735065f) {
          if (x[0] <= -0.72162992f) {
            if (x[5] <= 0.24373564f) {
              if (x[0] <= -0.73141596f) {
                return 0.00000000f;
              } else {
                if (x[0] <= -0.72522229f) {
                  if (x[1] <= 0.54433589f) {
                    if (x[1] <= -0.76187220f) {
                      return 0.00364964f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.27777778f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              if (x[1] <= -0.10876816f) {
                if (x[1] <= -0.32646950f) {
                  if (x[1] <= -0.76187220f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= 0.28379829f) {
                      return 0.16279070f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  if (x[5] <= 0.25666028f) {
                    return 0.54545455f;
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[7] <= 0.19369143f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= 0.77525437f) {
                    if (x[7] <= 0.26920728f) {
                      return 0.33333333f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            }
          } else {
            if (x[5] <= 0.81868738f) {
              if (x[0] <= -0.71648917f) {
                if (x[1] <= 0.10893319f) {
                  if (x[0] <= -0.71902859f) {
                    if (x[5] <= 0.28477025f) {
                      return 0.00000000f;
                    } else {
                      return 0.07317073f;
                    }
                  } else {
                    if (x[5] <= -1.21392536f) {
                      return 0.40000000f;
                    } else {
                      return 0.04022989f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[1] <= -0.32646950f) {
                  return 0.00000000f;
                } else {
                  if (x[0] <= -0.71283489f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= 0.78156772f) {
                      return 0.00952381f;
                    } else {
                      return 0.14035088f;
                    }
                  }
                }
              }
            } else {
              return 0.00000000f;
            }
          }
        } else {
          if (x[0] <= -0.69487315f) {
            if (x[6] <= 0.30974765f) {
              return 0.00000000f;
            } else {
              if (x[1] <= -0.10876816f) {
                return 0.35483871f;
              } else {
                if (x[5] <= 0.89972594f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= 0.90655741f) {
                    return 0.69230769f;
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            }
          } else {
            if (x[6] <= -0.36989510f) {
              return 0.00000000f;
            } else {
              if (x[7] <= 0.34472315f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[5] <= 0.16493605f) {
                  return 0.41666667f;
                } else {
                  return 0.00000000f;
                }
              }
            }
          }
        }
      } else {
        if (x[7] <= 4.72464323f) {
          if (x[1] <= -0.21761883f) {
            if (x[0] <= -0.69115695f) {
              return 0.00000000f;
            } else {
              return 0.71428571f;
            }
          } else {
            return 0.00000000f;
          }
        } else {
          return 0.00000000f;
        }
      }
    } else {
      if (x[7] <= 1.15425318f) {
        if (x[0] <= -0.67325717f) {
          if (x[6] <= -0.20627740f) {
            if (x[6] <= -0.36989510f) {
              if (x[0] <= -0.67567271f) {
                return 0.00000000f;
              } else {
                if (x[1] <= 0.10893319f) {
                  return 0.00000000f;
                } else {
                  return 0.50000000f;
                }
              }
            } else {
              if (x[1] <= 0.54433589f) {
                if (x[0] <= -0.67567271f) {
                  return 0.53333333f;
                } else {
                  return 0.95454545f;
                }
              } else {
                return 0.00000000f;
              }
            }
          } else {
            if (x[5] <= 1.40697235f) {
              if (x[7] <= -0.30068575f) {
                if (x[0] <= -0.67567271f) {
                  if (x[5] <= 1.28126943f) {
                    if (x[7] <= -0.31327173f) {
                      return 0.00495050f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    if (x[1] <= -0.54417084f) {
                      return 0.40000000f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  if (x[5] <= -0.27370565f) {
                    if (x[5] <= -0.51440006f) {
                      return 0.09210526f;
                    } else {
                      return 0.57142857f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[1] <= -0.10876816f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= -0.42661697f) {
                    return 0.68421053f;
                  } else {
                    if (x[7] <= -0.23423179f) {
                      return 0.00000000f;
                    } else {
                      return 0.12000000f;
                    }
                  }
                }
              }
            } else {
              if (x[6] <= 0.28457570f) {
                return 0.50000000f;
              } else {
                if (x[0] <= -0.67567271f) {
                  return 0.60606061f;
                } else {
                  if (x[1] <= 0.10893319f) {
                    if (x[5] <= 1.40920299f) {
                      return 0.45454545f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            }
          }
        } else {
          if (x[1] <= 0.47031744f) {
            if (x[5] <= -1.33328980f) {
              if (x[1] <= -0.97957355f) {
                return 0.00000000f;
              } else {
                if (x[0] <= -0.63231683f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            } else {
              if (x[6] <= -0.61456648f) {
                if (x[0] <= 1.39302188f) {
                  if (x[1] <= 0.10893319f) {
                    return 0.00000000f;
                  } else {
                    if (x[6] <= -0.87333417f) {
                      return 0.03947368f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  if (x[0] <= 1.61754340f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[7] <= 0.96294636f) {
                      return 0.03141762f;
                    } else {
                      return 0.01333333f;
                    }
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[0] <= 1.76464367f) {
              if (x[7] <= 0.75351566f) {
                if (x[7] <= -0.06960721f) {
                  if (x[5] <= -1.17621732f) {
                    if (x[0] <= -0.63851053f) {
                      return 0.00000000f;
                    } else {
                      return 0.02693089f;
                    }
                  } else {
                    if (x[1] <= 0.76203725f) {
                      return 0.01862803f;
                    } else {
                      return 0.00220353f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[0] <= 1.28927749f) {
                  return 0.00000000f;
                } else {
                  return 0.16901408f;
                }
              }
            } else {
              if (x[5] <= -0.82190439f) {
                if (x[1] <= 0.84669888f) {
                  return 0.00000000f;
                } else {
                  return 0.55555556f;
                }
              } else {
                return 0.00000000f;
              }
            }
          }
        }
      } else {
        if (x[0] <= 1.22734052f) {
          if (x[6] <= -1.32038808f) {
            if (x[7] <= 1.56405264f) {
              return 0.00000000f;
            } else {
              if (x[0] <= -0.67325717f) {
                if (x[1] <= 0.10893319f) {
                  if (x[7] <= 2.29554951f) {
                    return 0.60000000f;
                  } else {
                    if (x[7] <= 4.18344617f) {
                      return 0.00000000f;
                    } else {
                      return 0.55555556f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[1] <= 1.63284260f) {
              if (x[1] <= 0.57916811f) {
                if (x[0] <= -0.66656798f) {
                  if (x[5] <= -0.22601287f) {
                    return 0.00000000f;
                  } else {
                    return 0.33333333f;
                  }
                } else {
                  if (x[7] <= 1.19402486f) {
                    if (x[7] <= 1.18496299f) {
                      return 0.00000000f;
                    } else {
                      return 0.06349206f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[7] <= 1.25896853f) {
                  return 0.00000000f;
                } else {
                  if (x[7] <= 1.27608544f) {
                    return 0.53846154f;
                  } else {
                    if (x[5] <= -1.22450197f) {
                      return 0.58333333f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              }
            } else {
              if (x[0] <= -0.13527269f) {
                return 0.00000000f;
              } else {
                return 0.56250000f;
              }
            }
          }
        } else {
          if (x[0] <= 1.75225627f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      }
    }
  } else {
    if (x[3] <= -1.51086811f) {
      if (x[4] <= 4.50143015f) {
        if (x[6] <= 0.00768421f) {
          if (x[7] <= 1.02436590f) {
            if (x[1] <= -0.10876816f) {
              if (x[6] <= -0.99919394f) {
                return 0.80000000f;
              } else {
                if (x[5] <= 1.40015209f) {
                  if (x[7] <= 0.44541097f) {
                    return 0.00000000f;
                  } else {
                    if (x[6] <= -0.49575487f) {
                      return 0.00000000f;
                    } else {
                      return 0.53846154f;
                    }
                  }
                } else {
                  return 0.62500000f;
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[6] <= -3.31501377f) {
              return 0.00000000f;
            } else {
              if (x[6] <= -3.27725577f) {
                return 0.64285714f;
              } else {
                if (x[4] <= 2.56777543f) {
                  if (x[7] <= 1.42711717f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= -1.27183217f) {
                      return 0.21153846f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              }
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[3] <= -21.16181755f) {
          return 0.00000000f;
        } else {
          if (x[7] <= -0.18388789f) {
            if (x[0] <= 0.90681672f) {
              return 1.00000000f;
            } else {
              if (x[5] <= -0.96285707f) {
                if (x[0] <= 1.25521213f) {
                  return 0.96000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_031(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_032(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_033(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_034(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_035(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_036(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[6] <= -1.15425318f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[1] <= -0.84653383f) {
      if (x[5] <= -1.37666649f) {
        if (x[4] <= 2.56777543f) {
          if (x[5] <= -1.40445602f) {
            if (x[0] <= 1.64696342f) {
              if (x[3] <= 0.00074339f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 0.84615385f;
            }
          } else {
            if (x[5] <= -1.39416128f) {
              return 0.58333333f;
            } else {
              return 0.20000000f;
            }
          }
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[3] <= -1.51086811f) {
          if (x[4] <= 4.50143015f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[0] <= -0.65089792f) {
        if (x[4] <= 2.56777543f) {
          if (x[6] <= -5.37911391f) {
            if (x[3] <= 0.00074339f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[5] <= -0.25625467f) {
              if (x[3] <= 0.00074339f) {
                if (x[0] <= -0.65709162f) {
                  if (x[0] <= -0.68186641f) {
                    if (x[5] <= -0.83667621f) {
                      return 0.11428571f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[6] <= -1.88021231f) {
                    return 0.66666667f;
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[6] <= -0.99919394f) {
                if (x[3] <= 0.00074339f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[5] <= -0.22967107f) {
                  if (x[1] <= -0.32646950f) {
                    return 1.00000000f;
                  } else {
                    if (x[1] <= -0.10876816f) {
                      return 0.97222222f;
                    } else {
                      return 0.98969072f;
                    }
                  }
                } else {
                  if (x[5] <= 1.40713775f) {
                    if (x[5] <= 1.40683144f) {
                      return 0.92182891f;
                    } else {
                      return 0.37500000f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[7] <= 3.36535764f) {
          if (x[0] <= -0.59515464f) {
            if (x[3] <= -1.51086811f) {
              if (x[1] <= 0.32663454f) {
                if (x[5] <= -0.28204234f) {
                  if (x[5] <= -1.41096312f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= -0.32646950f) {
                      return 0.28703704f;
                    } else {
                      return 0.41650854f;
                    }
                  }
                } else {
                  if (x[0] <= -0.60134834f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[6] <= 0.30974765f) {
                      return 0.00000000f;
                    } else {
                      return 0.09909910f;
                    }
                  }
                }
              } else {
                if (x[0] <= -0.64780107f) {
                  if (x[1] <= 0.87088794f) {
                    if (x[7] <= -0.30974765f) {
                      return 0.17647059f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.57142857f;
                  }
                } else {
                  if (x[7] <= -0.13354398f) {
                    if (x[5] <= 0.55268463f) {
                      return 0.00000000f;
                    } else {
                      return 0.19879518f;
                    }
                  } else {
                    if (x[7] <= -0.10837203f) {
                      return 0.81818182f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              }
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[4] <= 2.56777543f) {
              if (x[0] <= 1.63147920f) {
                if (x[3] <= 0.00074339f) {
                  if (x[6] <= -3.20173991f) {
                    return 0.62500000f;
                  } else {
                    if (x[6] <= 0.00768421f) {
                      return 0.07279693f;
                    } else {
                      return 0.00509338f;
                    }
                  }
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[3] <= 0.00074339f) {
                  if (x[1] <= -0.19342980f) {
                    if (x[0] <= 1.73986888f) {
                      return 0.02884615f;
                    } else {
                      return 0.20000000f;
                    }
                  } else {
                    if (x[1] <= 0.08474415f) {
                      return 0.03356164f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[4] <= 15.13653183f) {
                if (x[3] <= -4.53409100f) {
                  if (x[4] <= 6.43508506f) {
                    if (x[0] <= 1.58967173f) {
                      return 0.00000000f;
                    } else {
                      return 0.12162162f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  return 1.00000000f;
                }
              } else {
                return 0.91304348f;
              }
            }
          }
        } else {
          if (x[5] <= -0.16320197f) {
            if (x[5] <= -0.16771895f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 0.33333333f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      }
    }
  }
}

static float rf_tree_037(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_038(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_039(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[1] <= 0.73784819f) {
      if (x[5] <= -1.29847133f) {
        if (x[5] <= -1.29864776f) {
          if (x[4] <= 2.56777543f) {
            if (x[6] <= -10.36316109f) {
              return 0.82352941f;
            } else {
              if (x[7] <= 7.15373683f) {
                if (x[7] <= 3.08846605f) {
                  if (x[6] <= -2.66054296f) {
                    if (x[6] <= -2.86191857f) {
                      return 0.96296296f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[1] <= -1.41497624f) {
                      return 0.83333333f;
                    } else {
                      return 0.91355018f;
                    }
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[6] <= -8.65146780f) {
                  if (x[7] <= 9.43179846f) {
                    return 0.93548387f;
                  } else {
                    return 0.96551724f;
                  }
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[6] <= -0.42023902f) {
              if (x[3] <= -4.53409100f) {
                if (x[5] <= -1.37428045f) {
                  return 0.00000000f;
                } else {
                  return 0.53846154f;
                }
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          return 0.64285714f;
        }
      } else {
        if (x[1] <= -0.08457912f) {
          if (x[3] <= -1.51086811f) {
            if (x[4] <= 4.50143015f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[5] <= -0.93957141f) {
                if (x[0] <= 0.78913647f) {
                  return 1.00000000f;
                } else {
                  return 0.98581560f;
                }
              } else {
                return 1.00000000f;
              }
            }
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_040(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[4] <= 0.63412052f) {
      if (x[7] <= 1.15425318f) {
        if (x[1] <= 0.30244550f) {
          if (x[0] <= -0.69115695f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[6] <= 0.30068575f) {
              if (x[0] <= -0.64495197f) {
                if (x[1] <= -0.32646950f) {
                  if (x[6] <= -0.19369143f) {
                    if (x[5] <= -1.40824115f) {
                      return 0.46666667f;
                    } else {
                      return 0.03333333f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[0] <= -0.66018847f) {
                    if (x[1] <= 0.10893319f) {
                      return 0.06184586f;
                    } else {
                      return 0.10843373f;
                    }
                  } else {
                    if (x[6] <= -0.08746578f) {
                      return 0.06983240f;
                    } else {
                      return 0.17560976f;
                    }
                  }
                }
              } else {
                if (x[1] <= 0.19359483f) {
                  if (x[6] <= 0.29162385f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[1] <= -0.10876816f) {
                      return 0.16564417f;
                    } else {
                      return 0.06714286f;
                    }
                  }
                } else {
                  if (x[5] <= -0.70724931f) {
                    if (x[7] <= 0.47058292f) {
                      return 0.07407407f;
                    } else {
                      return 0.40625000f;
                    }
                  } else {
                    if (x[7] <= -0.20905984f) {
                      return 0.21590909f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[6] <= -0.87333417f) {
            if (x[5] <= -0.88080716f) {
              return 0.00000000f;
            } else {
              if (x[5] <= -0.85748810f) {
                return 0.63636364f;
              } else {
                if (x[7] <= 0.88894078f) {
                  if (x[5] <= -0.23709705f) {
                    return 0.44444444f;
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[1] <= 1.74169332f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= 1.98987281f) {
                      return 0.54545455f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[0] <= -0.49141023f) {
          if (x[6] <= -4.09534431f) {
            if (x[7] <= 4.37223577f) {
              if (x[0] <= -0.67412427f) {
                if (x[1] <= 0.10893319f) {
                  if (x[0] <= -0.68496326f) {
                    return 0.00000000f;
                  } else {
                    return 0.91666667f;
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[1] <= 0.10893319f) {
                  if (x[6] <= -4.23379016f) {
                    return 0.00000000f;
                  } else {
                    return 0.60000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              if (x[6] <= -7.19149446f) {
                if (x[5] <= -0.98904374f) {
                  if (x[0] <= -0.65399477f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= 0.10893319f) {
                      return 0.00000000f;
                    } else {
                      return 0.57142857f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                return 0.00000000f;
              }
            }
          } else {
            if (x[7] <= 1.20056957f) {
              if (x[1] <= -0.10876816f) {
                return 0.33333333f;
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[1] <= 0.32663454f) {
                if (x[0] <= -0.65709162f) {
                  if (x[6] <= -1.65366477f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= -0.10876816f) {
                      return 0.05208333f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  if (x[6] <= -1.56405264f) {
                    if (x[5] <= -1.41321206f) {
                      return 0.40000000f;
                    } else {
                      return 0.04368932f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[6] <= -1.27608544f) {
                  return 0.00000000f;
                } else {
                  if (x[1] <= 0.76203725f) {
                    return 0.04761905f;
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            }
          }
        } else {
          if (x[5] <= -1.16844296f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_041(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_042(const float* x) {
  if (x[6] <= 0.24832809f) {
    if (x[5] <= -0.86181006f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[1] <= 0.47031744f) {
        if (x[0] <= -0.67839792f) {
          if (x[5] <= -0.80433607f) {
            if (x[0] <= -0.73141596f) {
              if (x[5] <= -1.28380829f) {
                return 0.00000000f;
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[4] <= 2.56777543f) {
                if (x[5] <= -1.28846639f) {
                  return 0.00000000f;
                } else {
                  if (x[7] <= -0.30974765f) {
                    if (x[0] <= -0.71593174f) {
                      return 0.01244813f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[0] <= -0.72162992f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[4] <= 2.56777543f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[5] <= 0.85759640f) {
                  if (x[3] <= -1.51086811f) {
                    if (x[5] <= -0.57541543f) {
                      return 0.96774194f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[0] <= -0.70354435f) {
                    return 0.89473684f;
                  } else {
                    if (x[1] <= 0.10893319f) {
                      return 1.00000000f;
                    } else {
                      return 0.99722222f;
                    }
                  }
                }
              }
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[5] <= -1.17593098f) {
            if (x[0] <= -0.28856668f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[1] <= 0.76203725f) {
                if (x[5] <= -1.20461524f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= -1.19063491f) {
                    return 0.77272727f;
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[5] <= -1.19204783f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= -1.18971741f) {
                    return 0.60000000f;
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            }
          } else {
            if (x[5] <= 1.40879184f) {
              if (x[6] <= 0.31327173f) {
                return 0.00000000f;
              } else {
                if (x[0] <= 1.76464367f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[1] <= 1.17325091f) {
                    return 0.00000000f;
                  } else {
                    return 0.50000000f;
                  }
                }
              }
            } else {
              return 0.02608696f;
            }
          }
        } else {
          if (x[1] <= 0.97973862f) {
            if (x[0] <= 1.51534742f) {
              if (x[5] <= -0.43290903f) {
                if (x[3] <= -1.51086811f) {
                  return 0.50000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 1.00000000f;
              }
            } else {
              return 0.98198198f;
            }
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_043(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[5] <= 1.40457731f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_044(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_045(const float* x) {
  if (x[1] <= 0.47031744f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[0] <= -0.56418616f) {
      if (x[3] <= 1.51235481f) {
        if (x[0] <= -0.66947901f) {
          if (x[3] <= -1.51086811f) {
            if (x[0] <= -0.67567271f) {
              return 0.62962963f;
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[6] <= -1.55499071f) {
            if (x[4] <= 2.56777543f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[5] <= -1.40938836f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 0.63412052f) {
        if (x[6] <= -1.02436590f) {
          if (x[5] <= 0.99685660f) {
            if (x[6] <= -3.13881004f) {
              if (x[6] <= -3.17958868f) {
                if (x[5] <= -1.20713288f) {
                  if (x[7] <= 5.32876992f) {
                    return 0.69230769f;
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                return 0.86666667f;
              }
            } else {
              if (x[0] <= -0.05010937f) {
                return 0.09375000f;
              } else {
                return 0.00000000f;
              }
            }
          } else {
            if (x[0] <= 0.36331987f) {
              if (x[6] <= -4.25896192f) {
                return 0.00000000f;
              } else {
                if (x[1] <= 1.19743997f) {
                  return 0.00000000f;
                } else {
                  if (x[7] <= 2.20744777f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= 1.34711754f) {
                      return 0.38461538f;
                    } else {
                      return 0.75000000f;
                    }
                  }
                }
              }
            } else {
              if (x[7] <= 1.32642937f) {
                return 0.84615385f;
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        } else {
          if (x[5] <= -1.19059002f) {
            if (x[6] <= 0.31327173f) {
              return 0.00000000f;
            } else {
              if (x[1] <= 0.76203725f) {
                if (x[0] <= 0.39583677f) {
                  if (x[5] <= -1.20555645f) {
                    return 0.00000000f;
                  } else {
                    return 0.61111111f;
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                return 0.01234568f;
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[3] <= -1.51086811f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          return 1.00000000f;
        }
      }
    }
  }
}

static float rf_tree_046(const float* x) {
  if (x[7] <= -0.24832809f) {
    if (x[3] <= 1.51235481f) {
      if (x[6] <= 0.26997598f) {
        return 0.00000000f;
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[0] <= 0.71636054f) {
            if (x[3] <= -4.53409100f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[5] <= -0.09957463f) {
              if (x[1] <= -0.30228046f) {
                if (x[1] <= -0.76187220f) {
                  return 1.00000000f;
                } else {
                  if (x[3] <= -1.51086811f) {
                    return 0.96000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[0] <= 0.72719952f) {
                  return 0.87179487f;
                } else {
                  if (x[5] <= -0.10755785f) {
                    if (x[0] <= 1.77049327f) {
                      return 0.99634035f;
                    } else {
                      return 0.99308198f;
                    }
                  } else {
                    return 0.95744681f;
                  }
                }
              }
            } else {
              if (x[0] <= 1.58192962f) {
                if (x[3] <= -4.53409100f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[7] <= -0.30974765f) {
                  if (x[5] <= 1.40384251f) {
                    if (x[5] <= 0.77518386f) {
                      return 1.00000000f;
                    } else {
                      return 0.99853372f;
                    }
                  } else {
                    return 0.97297297f;
                  }
                } else {
                  if (x[3] <= -1.51086811f) {
                    return 0.93333333f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            }
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_047(const float* x) {
  if (x[0] <= -0.68496326f) {
    if (x[1] <= -0.47015239f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 0.63412052f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_048(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[3] <= -7.55731416f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 2.56777543f) {
        if (x[0] <= -0.68496326f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[1] <= 0.47031744f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[0] <= 1.38682818f) {
              if (x[6] <= -1.25896853f) {
                if (x[0] <= -0.48831338f) {
                  if (x[0] <= -0.64780107f) {
                    return 0.00711744f;
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[5] <= 1.38626993f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[3] <= -1.51086811f) {
                      return 0.00000000f;
                    } else {
                      return 0.64285714f;
                    }
                  }
                }
              } else {
                if (x[1] <= 0.76203725f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      } else {
        if (x[6] <= -8.65146828f) {
          if (x[3] <= -1.51086811f) {
            return 0.63636364f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[0] <= 1.25985742f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[3] <= -4.53409100f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          }
        }
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_049(const float* x) {
  if (x[0] <= -0.68496326f) {
    if (x[5] <= 0.19280723f) {
      if (x[0] <= -0.69115695f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[4] <= 0.63412052f) {
          if (x[0] <= -0.68818396f) {
            if (x[6] <= 0.30974765f) {
              if (x[6] <= -2.68571496f) {
                return 0.16666667f;
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[5] <= -0.37491436f) {
                if (x[5] <= -0.69211161f) {
                  return 0.00000000f;
                } else {
                  return 0.57142857f;
                }
              } else {
                return 0.00000000f;
              }
            }
          } else {
            if (x[1] <= -0.10876816f) {
              if (x[1] <= -0.32646950f) {
                return 0.00000000f;
              } else {
                if (x[6] <= 0.30974765f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= -0.72391331f) {
                    return 0.00000000f;
                  } else {
                    return 0.78571429f;
                  }
                }
              }
            } else {
              return 0.00000000f;
            }
          }
        } else {
          if (x[3] <= -1.51086811f) {
            if (x[7] <= -0.24681777f) {
              return 0.55882353f;
            } else {
              if (x[6] <= -2.39623737f) {
                return 0.50000000f;
              } else {
                return 0.00000000f;
              }
            }
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_050(const float* x) {
  if (x[6] <= 0.30068575f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[5] <= -0.85791457f) {
        if (x[1] <= -0.51998182f) {
          if (x[1] <= -0.95538449f) {
            if (x[4] <= 2.56777543f) {
              if (x[1] <= -1.41497624f) {
                return 0.00000000f;
              } else {
                return 0.00532946f;
              }
            } else {
              if (x[0] <= -0.65709162f) {
                if (x[5] <= -1.30248237f) {
                  return 0.95238095f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[4] <= 2.56777543f) {
              return 0.00934579f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[0] <= -0.66328532f) {
            if (x[5] <= -1.25582170f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_051(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_052(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_053(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_054(const float* x) {
  if (x[7] <= -0.24832809f) {
    if (x[3] <= 1.51235481f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_055(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[0] <= -0.67839792f) {
      if (x[0] <= -0.69115695f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[3] <= 1.51235481f) {
          if (x[4] <= 2.56777543f) {
            if (x[6] <= -4.53585362f) {
              if (x[7] <= 6.23496032f) {
                return 0.50000000f;
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[4] <= 0.63412052f) {
                if (x[5] <= -0.61183414f) {
                  return 0.00000000f;
                } else {
                  if (x[7] <= -0.15871593f) {
                    return 0.01134522f;
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                return 0.00000000f;
              }
            }
          } else {
            return 1.00000000f;
          }
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[0] <= -0.68496326f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[0] <= -0.68186641f) {
          if (x[4] <= 2.56777543f) {
            if (x[6] <= 0.20905984f) {
              if (x[5] <= 1.04129738f) {
                if (x[5] <= -0.83465540f) {
                  if (x[7] <= 0.48316889f) {
                    return 0.90000000f;
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[7] <= -0.12095800f) {
                    return 0.27272727f;
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                return 0.77272727f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[1] <= 0.47031744f) {
            if (x[4] <= 2.56777543f) {
              if (x[5] <= -1.09395003f) {
                if (x[3] <= -1.51086811f) {
                  if (x[6] <= -0.34472315f) {
                    if (x[6] <= -0.36989510f) {
                      return 0.00000000f;
                    } else {
                      return 0.57142857f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[0] <= -0.60444519f) {
                  if (x[0] <= -0.67325717f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[1] <= 0.32663454f) {
                      return 0.03380049f;
                    } else {
                      return 0.01424555f;
                    }
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_056(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_057(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[1] <= -0.47015239f) {
      if (x[0] <= -0.67839792f) {
        if (x[4] <= 2.56777543f) {
          if (x[1] <= -0.94038731f) {
            return 0.00000000f;
          } else {
            if (x[7] <= 4.56102538f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[7] <= 5.10222244f) {
                return 0.50000000f;
              } else {
                return 0.00000000f;
              }
            }
          }
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_058(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[5] <= -1.41386813f) {
      if (x[3] <= -1.51086811f) {
        if (x[0] <= -0.65399477f) {
          return 0.50000000f;
        } else {
          return 0.00000000f;
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[3] <= -1.51086811f) {
        if (x[4] <= 4.50143015f) {
          if (x[6] <= 0.08320007f) {
            if (x[6] <= -0.77264637f) {
              if (x[7] <= 1.09988177f) {
                if (x[7] <= 1.07470977f) {
                  if (x[5] <= -0.67932397f) {
                    if (x[1] <= -0.10876816f) {
                      return 0.22222222f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 0.25000000f;
                }
              } else {
                if (x[5] <= 0.16070870f) {
                  if (x[5] <= 0.14398815f) {
                    if (x[5] <= -0.29234950f) {
                      return 0.00000000f;
                    } else {
                      return 0.08928571f;
                    }
                  } else {
                    return 0.57142857f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              if (x[5] <= -1.40907586f) {
                if (x[6] <= -0.09300361f) {
                  return 0.70000000f;
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[5] <= 0.36993931f) {
              if (x[0] <= 1.77049327f) {
                if (x[0] <= -0.63851053f) {
                  return 0.00000000f;
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[5] <= 0.31705990f) {
                  if (x[7] <= -0.30974765f) {
                    return 0.01166181f;
                  } else {
                    if (x[6] <= 0.28457570f) {
                      return 0.00000000f;
                    } else {
                      return 0.30303030f;
                    }
                  }
                } else {
                  return 0.71428571f;
                }
              }
            } else {
              return 0.00000000f;
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_059(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[1] <= -0.19342980f) {
      if (x[3] <= -1.51086811f) {
        if (x[3] <= -10.58053732f) {
          return 1.00000000f;
        } else {
          if (x[7] <= -0.13354398f) {
            if (x[0] <= 1.66554457f) {
              if (x[6] <= 0.20905984f) {
                if (x[6] <= 0.18388789f) {
                  return 0.00000000f;
                } else {
                  return 0.20689655f;
                }
              } else {
                if (x[4] <= 4.50143015f) {
                  if (x[4] <= 2.56777543f) {
                    if (x[0] <= 1.45805573f) {
                      return 0.00000000f;
                    } else {
                      return 0.06315789f;
                    }
                  } else {
                    if (x[6] <= 0.30974765f) {
                      return 0.00000000f;
                    } else {
                      return 0.13043478f;
                    }
                  }
                } else {
                  if (x[1] <= -0.32646950f) {
                    if (x[5] <= -1.23859030f) {
                      return 0.89655172f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[6] <= -8.89060116f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  }
}

static float rf_tree_060(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_061(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[0] <= -0.68496326f) {
        if (x[1] <= 0.32663454f) {
          if (x[4] <= 2.56777543f) {
            if (x[7] <= 2.63537097f) {
              if (x[6] <= -0.21886338f) {
                return 0.00000000f;
              } else {
                if (x[7] <= 0.19570518f) {
                  if (x[1] <= -0.10876816f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  return 0.33333333f;
                }
              }
            } else {
              if (x[1] <= -0.32646950f) {
                if (x[6] <= -2.68571484f) {
                  return 0.00000000f;
                } else {
                  return 0.55555556f;
                }
              } else {
                return 0.00000000f;
              }
            }
          } else {
            if (x[0] <= -0.71593174f) {
              if (x[0] <= -0.71902859f) {
                return 1.00000000f;
              } else {
                return 0.99038462f;
              }
            } else {
              if (x[0] <= -0.69115695f) {
                return 1.00000000f;
              } else {
                if (x[7] <= -0.30974765f) {
                  return 0.99850969f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        } else {
          if (x[1] <= 0.76203725f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[0] <= -0.70979998f) {
              if (x[1] <= 0.94055232f) {
                if (x[5] <= 0.19564788f) {
                  return 0.02380952f;
                } else {
                  if (x[6] <= 0.19647386f) {
                    return 0.00000000f;
                  } else {
                    if (x[0] <= -0.72677070f) {
                      return 0.00000000f;
                    } else {
                      return 0.66666667f;
                    }
                  }
                }
              } else {
                if (x[0] <= -0.71283489f) {
                  return 0.00000000f;
                } else {
                  return 0.57142857f;
                }
              }
            } else {
              if (x[4] <= 0.63412052f) {
                return 0.00000000f;
              } else {
                return 0.94736842f;
              }
            }
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_062(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_063(const float* x) {
  if (x[0] <= -0.68496326f) {
    if (x[0] <= -0.72831911f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[5] <= 1.20154476f) {
        if (x[7] <= -0.31327173f) {
          if (x[5] <= 0.22164509f) {
            if (x[0] <= -0.69115695f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[0] <= -0.68818396f) {
                if (x[5] <= -0.24494199f) {
                  if (x[4] <= 0.63412052f) {
                    return 0.37500000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[1] <= -0.47015239f) {
              if (x[4] <= 0.63412052f) {
                if (x[5] <= 1.09034413f) {
                  return 0.00000000f;
                } else {
                  if (x[1] <= -0.76187220f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= -0.57900307f) {
                      return 0.25000000f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[3] <= 1.51235481f) {
                if (x[1] <= 0.32663454f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[4] <= 2.56777543f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[4] <= 0.63412052f) {
            if (x[7] <= 4.62395525f) {
              if (x[5] <= 1.03344989f) {
                return 0.00000000f;
              } else {
                if (x[7] <= 2.61019897f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= 1.07167917f) {
                    return 0.57142857f;
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            } else {
              if (x[6] <= -5.10222244f) {
                return 0.00000000f;
              } else {
                return 0.66666667f;
              }
            }
          } else {
            if (x[3] <= -1.51086811f) {
              if (x[1] <= -0.10876816f) {
                return 0.72727273f;
              } else {
                return 0.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[7] <= 3.74293697f) {
          if (x[0] <= -0.69115695f) {
            return 0.00000000f;
          } else {
            if (x[4] <= 0.63412052f) {
              return 0.00000000f;
            } else {
              if (x[4] <= 2.56777543f) {
                return 0.88888889f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[5] <= 1.40399069f) {
            return 0.00000000f;
          } else {
            return 0.72727273f;
          }
        }
      }
    }
  } else {
    if (x[1] <= 0.47031744f) {
      if (x[0] <= -0.65678194f) {
        if (x[0] <= -0.66656798f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[4] <= 0.63412052f) {
            if (x[0] <= -0.66328532f) {
              if (x[5] <= -1.31844521f) {
                if (x[5] <= -1.32077706f) {
                  if (x[1] <= -0.32646950f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= -1.39292186f) {
                      return 0.00000000f;
                    } else {
                      return 0.20512821f;
                    }
                  }
                } else {
                  return 0.62500000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[1] <= -0.54417084f) {
              if (x[3] <= -1.51086811f) {
                if (x[5] <= 1.10842037f) {
                  if (x[1] <= -0.76187220f) {
                    return 0.00000000f;
                  } else {
                    if (x[7] <= -0.15871593f) {
                      return 0.37142857f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  return 0.54545455f;
                }
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[5] <= -1.40455151f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        }
      } else {
        if (x[4] <= 0.63412052f) {
          if (x[6] <= -4.08225489f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[3] <= 1.51235481f) {
        if (x[1] <= 0.84669888f) {
          if (x[1] <= 0.62899753f) {
            return 0.00000000f;
          } else {
            if (x[5] <= -1.41372466f) {
              if (x[4] <= 2.56777543f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[4] <= 2.56777543f) {
                if (x[7] <= 0.74747440f) {
                  if (x[3] <= -1.51086811f) {
                    return 0.00000000f;
                  } else {
                    if (x[0] <= -0.65709162f) {
                      return 0.00000000f;
                    } else {
                      return 0.01823417f;
                    }
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[3] <= -1.51086811f) {
                  return 0.95238095f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_064(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[3] <= -7.55731416f) {
      if (x[6] <= -0.69713050f) {
        return 0.69230769f;
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_065(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_066(const float* x) {
  if (x[0] <= -0.68496326f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_067(const float* x) {
  if (x[6] <= 0.24832809f) {
    if (x[1] <= -0.47015239f) {
      if (x[3] <= 1.51235481f) {
        if (x[4] <= 2.56777543f) {
          if (x[0] <= 0.16047631f) {
            if (x[1] <= -0.94038731f) {
              return 0.00000000f;
            } else {
              if (x[7] <= 4.46033764f) {
                if (x[5] <= -0.61166057f) {
                  return 0.00000000f;
                } else {
                  if (x[0] <= -0.68496326f) {
                    return 0.00000000f;
                  } else {
                    if (x[7] <= -0.15871593f) {
                      return 0.09090909f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              } else {
                if (x[5] <= -0.26730931f) {
                  if (x[7] <= 6.44892192f) {
                    return 0.50000000f;
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[7] <= 2.44658136f) {
            if (x[6] <= -0.77264637f) {
              return 1.00000000f;
            } else {
              if (x[5] <= 1.37970746f) {
                if (x[7] <= 0.69713050f) {
                  if (x[6] <= 0.09578605f) {
                    return 1.00000000f;
                  } else {
                    if (x[6] <= 0.13354398f) {
                      return 0.96875000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  return 0.97560976f;
                }
              } else {
                return 0.94736842f;
              }
            }
          } else {
            if (x[6] <= -2.87450445f) {
              return 0.99305556f;
            } else {
              return 0.93548387f;
            }
          }
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 0.63412052f) {
        if (x[0] <= 1.25676060f) {
          if (x[6] <= -0.43584563f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[6] <= -0.37442605f) {
              if (x[0] <= -0.68496326f) {
                return 0.00000000f;
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[5] <= -0.32622524f) {
                if (x[5] <= -0.33566321f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[0] <= -0.40624691f) {
                    return 0.90476190f;
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[5] <= 1.40019786f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[0] <= -0.66018847f) {
                    if (x[0] <= -0.66328532f) {
                      return 0.03448276f;
                    } else {
                      return 0.69230769f;
                    }
                  } else {
                    if (x[0] <= 0.60177718f) {
                      return 0.00000000f;
                    } else {
                      return 0.12500000f;
                    }
                  }
                }
              }
            }
          }
        } else {
          if (x[7] <= 5.89513898f) {
            if (x[7] <= -0.23926619f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[6] <= 0.20503233f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[0] <= 1.75965434f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= -1.40198606f) {
                    return 0.40000000f;
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[3] <= -1.51086811f) {
          if (x[3] <= -10.58053732f) {
            return 0.88000000f;
          } else {
            if (x[6] <= -4.09534431f) {
              if (x[5] <= -1.21657091f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[7] <= 3.26466978f) {
                if (x[0] <= -0.68496326f) {
                  if (x[0] <= -0.68806010f) {
                    return 0.40000000f;
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[0] <= 1.67173821f) {
                  return 0.00000000f;
                } else {
                  if (x[4] <= 4.50143015f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            }
          }
        } else {
          return 1.00000000f;
        }
      }
    }
  } else {
    if (x[7] <= -0.26997598f) {
      if (x[0] <= -0.67839792f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      return 0.00000000f;
    }
  }
}

static float rf_tree_068(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_069(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_070(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_071(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[7] <= -0.24832809f) {
      if (x[0] <= -0.67839792f) {
        if (x[4] <= 2.56777543f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[3] <= -4.53409100f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[0] <= -0.67325717f) {
          if (x[4] <= 2.56777543f) {
            if (x[7] <= -0.31327173f) {
              if (x[5] <= 1.39624637f) {
                if (x[3] <= -1.51086811f) {
                  return 0.00000000f;
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[3] <= -1.51086811f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= 1.40848672f) {
                    if (x[0] <= -0.67567271f) {
                      return 0.55932203f;
                    } else {
                      return 0.14285714f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[4] <= 4.50143015f) {
              if (x[0] <= -0.67567271f) {
                return 0.99502488f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[6] <= 0.26997598f) {
            return 0.00000000f;
          } else {
            if (x[0] <= -0.65678194f) {
              if (x[1] <= -0.47015239f) {
                if (x[4] <= 2.56777543f) {
                  if (x[0] <= -0.66947901f) {
                    return 0.00000000f;
                  } else {
                    if (x[0] <= -0.66501954f) {
                      return 0.08000000f;
                    } else {
                      return 0.00557012f;
                    }
                  }
                } else {
                  if (x[4] <= 4.50143015f) {
                    if (x[7] <= -0.30974765f) {
                      return 0.99673203f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[1] <= 0.47031744f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[5] <= 1.40345758f) {
                    if (x[4] <= 2.56777543f) {
                      return 0.00000000f;
                    } else {
                      return 0.98076923f;
                    }
                  } else {
                    if (x[4] <= 2.56777543f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      }
    } else {
      if (x[4] <= 2.56777543f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_072(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_073(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[7] <= -0.24832809f) {
      if (x[1] <= -0.47015239f) {
        if (x[7] <= -0.30068575f) {
          if (x[3] <= -1.51086811f) {
            if (x[5] <= 0.12215401f) {
              if (x[1] <= -0.76187220f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              return 0.17777778f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[6] <= 0.26997598f) {
            return 0.00000000f;
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[1] <= 0.47031744f) {
          if (x[1] <= 0.30244550f) {
            if (x[5] <= -0.88556126f) {
              if (x[4] <= 2.56777543f) {
                if (x[3] <= -1.51086811f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= -0.99916896f) {
                    if (x[0] <= -0.67876956f) {
                      return 0.00080972f;
                    } else {
                      return 0.05730680f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                if (x[0] <= -0.65089792f) {
                  if (x[5] <= -1.29425603f) {
                    if (x[0] <= -0.68806010f) {
                      return 0.95454545f;
                    } else {
                      return 0.99876923f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[5] <= -1.27664822f) {
                    if (x[3] <= -4.53409100f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[5] <= -1.27571464f) {
                      return 0.82352941f;
                    } else {
                      return 0.99417023f;
                    }
                  }
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[5] <= 0.16493025f) {
            if (x[1] <= 0.73784819f) {
              if (x[4] <= 2.56777543f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[0] <= -0.65864006f) {
                  return 0.96842105f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[1] <= 1.41078728f) {
                if (x[3] <= -1.51086811f) {
                  if (x[1] <= 1.19743997f) {
                    return 0.42857143f;
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[4] <= 1.60094798f) {
                    if (x[1] <= 1.19743997f) {
                      return 0.00582411f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[0] <= -0.64160737f) {
                  if (x[5] <= -0.32131311f) {
                    if (x[5] <= -1.14744031f) {
                      return 0.00666667f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    if (x[1] <= 1.63284260f) {
                      return 0.00000000f;
                    } else {
                      return 0.07070707f;
                    }
                  }
                } else {
                  if (x[4] <= 2.56777543f) {
                    if (x[6] <= 0.31327173f) {
                      return 0.00000000f;
                    } else {
                      return 0.00746733f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            }
          } else {
            if (x[1] <= 0.94055232f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[6] <= 0.31327173f) {
                return 0.00000000f;
              } else {
                if (x[0] <= -0.67567271f) {
                  if (x[5] <= 0.44691958f) {
                    return 0.03205128f;
                  } else {
                    if (x[0] <= -0.68663555f) {
                      return 0.00000000f;
                    } else {
                      return 0.00492611f;
                    }
                  }
                } else {
                  if (x[0] <= -0.66018847f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            }
          }
        }
      }
    } else {
      if (x[5] <= -0.85939577f) {
        if (x[0] <= 0.53519493f) {
          if (x[0] <= -0.66328532f) {
            if (x[4] <= 2.56777543f) {
              if (x[6] <= 0.18388789f) {
                return 0.00000000f;
              } else {
                if (x[1] <= -0.21761883f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= -0.88519785f) {
                    return 0.00000000f;
                  } else {
                    return 0.42857143f;
                  }
                }
              }
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[0] <= -0.63851053f) {
              if (x[1] <= 0.54433589f) {
                if (x[5] <= -0.89627391f) {
                  if (x[7] <= 0.24403533f) {
                    if (x[5] <= -1.24679697f) {
                      return 0.69820717f;
                    } else {
                      return 0.24896266f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  if (x[1] <= 0.10893319f) {
                    if (x[0] <= -0.64470422f) {
                      return 0.97674419f;
                    } else {
                      return 0.95833333f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                if (x[4] <= 2.56777543f) {
                  if (x[7] <= 0.36989510f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= 0.97973862f) {
                      return 0.00000000f;
                    } else {
                      return 0.05208333f;
                    }
                  }
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[5] <= -1.26564538f) {
                if (x[0] <= -0.63386527f) {
                  if (x[5] <= -1.28541750f) {
                    if (x[7] <= 2.18227577f) {
                      return 0.00000000f;
                    } else {
                      return 0.72727273f;
                    }
                  } else {
                    if (x[1] <= 0.43548523f) {
                      return 0.00000000f;
                    } else {
                      return 0.81250000f;
                    }
                  }
                } else {
                  if (x[4] <= 0.63412052f) {
                    return 0.00000000f;
                  } else {
                    return 0.50000000f;
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        } else {
          if (x[5] <= -1.40150833f) {
            if (x[1] <= -0.08457912f) {
              if (x[0] <= 1.71509409f) {
                return 0.00000000f;
              } else {
                return 0.40000000f;
              }
            } else {
              if (x[7] <= 6.05875683f) {
                if (x[0] <= 1.65780240f) {
                  return 0.00000000f;
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[4] <= 2.56777543f) {
                  if (x[7] <= 9.11714888f) {
                    return 0.61538462f;
                  } else {
                    return 0.73333333f;
                  }
                } else {
                  return 0.98648649f;
                }
              }
            }
          } else {
            if (x[5] <= -1.01166087f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[4] <= 2.56777543f) {
                if (x[6] <= -5.78186536f) {
                  return 0.63157895f;
                } else {
                  if (x[7] <= 0.03510811f) {
                    if (x[0] <= 1.10811186f) {
                      return 0.12345679f;
                    } else {
                      return 0.39285714f;
                    }
                  } else {
                    if (x[6] <= -3.00036430f) {
                      return 0.18918919f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              } else {
                if (x[7] <= 4.87567496f) {
                  return 1.00000000f;
                } else {
                  if (x[6] <= -5.08963656f) {
                    return 1.00000000f;
                  } else {
                    return 0.95238095f;
                  }
                }
              }
            }
          }
        }
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[5] <= 1.27664369f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[3] <= -4.53409100f) {
            if (x[4] <= 6.43508506f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            return 1.00000000f;
          }
        }
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_074(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_075(const float* x) {
  if (x[0] <= -0.68496326f) {
    if (x[0] <= -0.69115695f) {
      if (x[3] <= 1.51235481f) {
        if (x[5] <= 0.19934492f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 0.63412052f) {
        if (x[6] <= -4.59878349f) {
          return 0.63636364f;
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[5] <= -0.83312148f) {
          if (x[5] <= -0.86750948f) {
            if (x[3] <= 1.51235481f) {
              if (x[6] <= 0.27198973f) {
                return 1.00000000f;
              } else {
                return 0.88235294f;
              }
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_076(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[3] <= 1.51235481f) {
      if (x[6] <= 0.30068575f) {
        if (x[5] <= 1.26555288f) {
          if (x[0] <= 0.80771759f) {
            if (x[5] <= -0.13810534f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[1] <= -0.94038731f) {
                if (x[0] <= -0.20650020f) {
                  return 0.00000000f;
                } else {
                  if (x[4] <= 0.63412052f) {
                    return 0.00000000f;
                  } else {
                    return 0.42857143f;
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[1] <= -0.94038731f) {
            if (x[4] <= 2.56777543f) {
              if (x[1] <= -1.41062218f) {
                return 0.00000000f;
              } else {
                if (x[1] <= -1.19727486f) {
                  if (x[0] <= 0.30293133f) {
                    return 0.00000000f;
                  } else {
                    return 0.70000000f;
                  }
                } else {
                  if (x[0] <= 0.53364652f) {
                    return 0.00000000f;
                  } else {
                    if (x[6] <= -0.24403533f) {
                      return 0.00000000f;
                    } else {
                      return 0.63636364f;
                    }
                  }
                }
              }
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[7] <= 8.57595205f) {
              if (x[0] <= -0.68508711f) {
                if (x[5] <= 1.40789700f) {
                  return 0.00000000f;
                } else {
                  if (x[0] <= -0.70472112f) {
                    return 0.00000000f;
                  } else {
                    return 0.42857143f;
                  }
                }
              } else {
                if (x[6] <= -1.30125743f) {
                  if (x[4] <= 1.60094798f) {
                    return 0.00000000f;
                  } else {
                    return 0.96666667f;
                  }
                } else {
                  if (x[0] <= -0.26998560f) {
                    if (x[4] <= 2.56777543f) {
                      return 0.00000000f;
                    } else {
                      return 0.97435897f;
                    }
                  } else {
                    if (x[0] <= 1.58812332f) {
                      return 0.68531469f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              }
            } else {
              if (x[5] <= 1.28952670f) {
                return 0.96428571f;
              } else {
                return 0.00000000f;
              }
            }
          }
        }
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[1] <= -0.76187220f) {
            return 1.00000000f;
          } else {
            if (x[0] <= 0.21157430f) {
              return 1.00000000f;
            } else {
              if (x[0] <= 0.33235139f) {
                return 0.94736842f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[1] <= 0.47031744f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_077(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_078(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[7] <= -0.24832809f) {
      if (x[0] <= -0.67839792f) {
        if (x[5] <= -0.79675099f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[1] <= 0.47031744f) {
          if (x[7] <= -0.26997598f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            return 0.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[0] <= -0.68496326f) {
        if (x[4] <= 2.56777543f) {
          if (x[7] <= 4.62194157f) {
            if (x[4] <= 0.63412052f) {
              if (x[7] <= 2.63537097f) {
                if (x[5] <= 0.70105988f) {
                  return 0.00000000f;
                } else {
                  return 0.00458482f;
                }
              } else {
                if (x[0] <= -0.69115695f) {
                  return 0.00000000f;
                } else {
                  if (x[1] <= -0.21761883f) {
                    if (x[6] <= -2.76123071f) {
                      return 0.00000000f;
                    } else {
                      return 0.60000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[6] <= -4.77498698f) {
              return 0.00000000f;
            } else {
              return 0.70000000f;
            }
          }
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_079(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[0] <= -0.68496326f) {
      if (x[0] <= -0.69735065f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[5] <= 0.77154833f) {
          if (x[1] <= -0.10876816f) {
            if (x[6] <= -4.53585362f) {
              return 0.38461538f;
            } else {
              if (x[5] <= -0.63523898f) {
                return 0.00000000f;
              } else {
                if (x[5] <= -0.63165763f) {
                  return 0.72727273f;
                } else {
                  if (x[7] <= -0.31327173f) {
                    if (x[5] <= -0.44062594f) {
                      return 0.05319149f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            }
          } else {
            return 0.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[0] <= 1.09572446f) {
        if (x[5] <= -1.37976074f) {
          if (x[5] <= -1.38003463f) {
            if (x[0] <= -0.63231683f) {
              if (x[1] <= 0.32663454f) {
                if (x[7] <= -0.10837203f) {
                  if (x[0] <= -0.64780107f) {
                    if (x[1] <= -0.32646950f) {
                      return 0.00870827f;
                    } else {
                      return 0.10553633f;
                    }
                  } else {
                    if (x[0] <= -0.63851053f) {
                      return 0.17155756f;
                    } else {
                      return 0.08571429f;
                    }
                  }
                } else {
                  if (x[6] <= -0.09300361f) {
                    if (x[0] <= -0.65089792f) {
                      return 0.30555556f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    if (x[1] <= -0.32646950f) {
                      return 0.00000000f;
                    } else {
                      return 0.56451613f;
                    }
                  }
                }
              } else {
                if (x[5] <= -1.38025856f) {
                  if (x[6] <= 0.07061410f) {
                    if (x[1] <= 0.97973862f) {
                      return 0.09677419f;
                    } else {
                      return 0.76923077f;
                    }
                  } else {
                    if (x[6] <= 0.30974765f) {
                      return 0.00000000f;
                    } else {
                      return 0.00962696f;
                    }
                  }
                } else {
                  return 0.50000000f;
                }
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[7] <= -0.23423179f) {
              if (x[0] <= -0.64005896f) {
                return 0.00000000f;
              } else {
                return 0.50000000f;
              }
            } else {
              return 0.84210526f;
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[5] <= 1.10346836f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[6] <= -5.89513898f) {
            if (x[7] <= 6.02099872f) {
              return 0.60000000f;
            } else {
              if (x[5] <= 1.27368808f) {
                return 0.00000000f;
              } else {
                if (x[7] <= 7.25442457f) {
                  if (x[7] <= 6.66288352f) {
                    return 0.00000000f;
                  } else {
                    return 0.62500000f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            if (x[6] <= -0.49575487f) {
              if (x[5] <= 1.17204493f) {
                if (x[0] <= 1.66674888f) {
                  return 0.57142857f;
                } else {
                  if (x[6] <= -1.95572817f) {
                    if (x[5] <= 1.16909301f) {
                      return 0.00000000f;
                    } else {
                      return 0.85714286f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[6] <= -4.62395525f) {
                  if (x[6] <= -4.66171336f) {
                    return 0.00000000f;
                  } else {
                    return 0.42857143f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              if (x[7] <= 0.47058292f) {
                if (x[5] <= 1.26189619f) {
                  if (x[6] <= -0.09300361f) {
                    if (x[7] <= 0.11817556f) {
                      return 0.58823529f;
                    } else {
                      return 0.06741573f;
                    }
                  } else {
                    if (x[0] <= 1.65006030f) {
                      return 0.00000000f;
                    } else {
                      return 0.03592423f;
                    }
                  }
                } else {
                  if (x[6] <= 0.18388789f) {
                    if (x[6] <= 0.15871593f) {
                      return 0.01023392f;
                    } else {
                      return 0.16666667f;
                    }
                  } else {
                    if (x[5] <= 1.38823891f) {
                      return 0.00000000f;
                    } else {
                      return 0.02040816f;
                    }
                  }
                }
              } else {
                return 0.28571429f;
              }
            }
          }
        }
      }
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_080(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[0] <= -0.68496326f) {
      if (x[5] <= 0.58298010f) {
        if (x[6] <= -4.63100362f) {
          if (x[0] <= -0.69115695f) {
            return 0.00000000f;
          } else {
            if (x[5] <= -0.46933010f) {
              return 0.00000000f;
            } else {
              return 0.50000000f;
            }
          }
        } else {
          if (x[0] <= -0.73655674f) {
            return 0.00000000f;
          } else {
            if (x[0] <= -0.70664120f) {
              if (x[7] <= -0.30974765f) {
                if (x[1] <= -0.94038731f) {
                  return 0.00000000f;
                } else {
                  if (x[0] <= -0.71283489f) {
                    if (x[1] <= -0.57900307f) {
                      return 0.02247191f;
                    } else {
                      return 0.00237812f;
                    }
                  } else {
                    if (x[1] <= 0.10893319f) {
                      return 0.01314060f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[1] <= -0.10876816f) {
                if (x[0] <= -0.69115695f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= -0.63559657f) {
                    return 0.00000000f;
                  } else {
                    if (x[7] <= -0.31327173f) {
                      return 0.02447552f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              } else {
                return 0.00000000f;
              }
            }
          }
        }
      } else {
        if (x[5] <= 0.58345595f) {
          return 0.70000000f;
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[5] <= -1.16099787f) {
        if (x[5] <= -1.16121995f) {
          if (x[7] <= -0.12196488f) {
            if (x[0] <= -0.63231683f) {
              if (x[5] <= -1.30843729f) {
                if (x[5] <= -1.30946147f) {
                  if (x[0] <= -0.64160737f) {
                    if (x[0] <= -0.66947901f) {
                      return 0.01483051f;
                    } else {
                      return 0.06260434f;
                    }
                  } else {
                    if (x[5] <= -1.40619290f) {
                      return 0.09365559f;
                    } else {
                      return 0.16469518f;
                    }
                  }
                } else {
                  if (x[1] <= 0.32663454f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= 0.54433589f) {
                      return 0.66666667f;
                    } else {
                      return 0.66666667f;
                    }
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[6] <= 0.24832809f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[7] <= -0.29162385f) {
                  if (x[5] <= -1.20570284f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[0] <= 0.38809466f) {
                      return 0.11216216f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            if (x[5] <= -1.41387862f) {
              return 0.75000000f;
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[1] <= -0.10876816f) {
            return 0.66666667f;
          } else {
            return 0.60869565f;
          }
        }
      } else {
        if (x[5] <= 0.51805294f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[5] <= 0.64050254f) {
            if (x[6] <= 0.10837203f) {
              if (x[6] <= -1.77952451f) {
                if (x[5] <= 0.63032871f) {
                  return 0.00000000f;
                } else {
                  if (x[7] <= 2.08158791f) {
                    return 0.66666667f;
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      }
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_081(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_082(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_083(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_084(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_085(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_086(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[6] <= -1.15425318f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[1] <= 16.10998201f) {
      if (x[5] <= -1.41379213f) {
        if (x[4] <= 2.56777543f) {
          if (x[5] <= -1.41379607f) {
            if (x[0] <= 1.62528551f) {
              if (x[3] <= 0.00074339f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 0.96875000f;
            }
          } else {
            return 0.60000000f;
          }
        } else {
          if (x[5] <= -1.41385192f) {
            return 1.00000000f;
          } else {
            if (x[1] <= -0.10876816f) {
              return 0.89285714f;
            } else {
              if (x[7] <= -0.08320007f) {
                return 1.00000000f;
              } else {
                return 0.93103448f;
              }
            }
          }
        }
      } else {
        if (x[1] <= -0.19342980f) {
          if (x[4] <= 2.56777543f) {
            if (x[6] <= -3.23949790f) {
              if (x[3] <= 0.00074339f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[5] <= 1.40934455f) {
                if (x[3] <= 0.00074339f) {
                  if (x[0] <= 1.73986888f) {
                    if (x[5] <= 1.40818715f) {
                      return 0.00585106f;
                    } else {
                      return 0.22222222f;
                    }
                  } else {
                    if (x[5] <= -0.77103090f) {
                      return 0.00000000f;
                    } else {
                      return 0.58333333f;
                    }
                  }
                } else {
                  return 1.00000000f;
                }
              } else {
                return 0.71428571f;
              }
            }
          } else {
            if (x[4] <= 4.50143015f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[5] <= -0.85422409f) {
                if (x[4] <= 6.43508506f) {
                  return 1.00000000f;
                } else {
                  if (x[6] <= 0.27198973f) {
                    return 1.00000000f;
                  } else {
                    if (x[3] <= 4.53557797f) {
                      return 0.99047619f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[4] <= 2.56777543f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[7] <= 0.42023902f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      }
    } else {
      return 0.64285714f;
    }
  }
}

static float rf_tree_087(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_088(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_089(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[7] <= 9.23042297f) {
      if (x[0] <= -0.66638216f) {
        if (x[5] <= 1.40935200f) {
          if (x[4] <= 2.56777543f) {
            if (x[6] <= -5.16515231f) {
              return 0.53846154f;
            } else {
              if (x[0] <= -0.70044750f) {
                if (x[7] <= 0.19369143f) {
                  return 0.91170431f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[6] <= 0.20905984f) {
                  if (x[1] <= -0.76187220f) {
                    if (x[7] <= 0.82299027f) {
                      return 0.78571429f;
                    } else {
                      return 0.54545455f;
                    }
                  } else {
                    if (x[3] <= 0.00074339f) {
                      return 0.13600000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  if (x[1] <= -0.54417084f) {
                    if (x[0] <= -0.68806010f) {
                      return 0.89795918f;
                    } else {
                      return 0.97674419f;
                    }
                  } else {
                    if (x[3] <= 0.00074339f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            }
          } else {
            if (x[7] <= 1.51521903f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[1] <= -0.10876816f) {
                if (x[3] <= -3.02247957f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          return 0.87096774f;
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[6] <= -9.31852484f) {
        if (x[3] <= -1.51086811f) {
          if (x[1] <= -0.10876816f) {
            return 0.53846154f;
          } else {
            return 0.00000000f;
          }
        } else {
          return 1.00000000f;
        }
      } else {
        return 0.69230769f;
      }
    }
  }
}

static float rf_tree_090(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[4] <= 0.63412052f) {
      if (x[7] <= 4.08225489f) {
        if (x[1] <= 0.30244550f) {
          if (x[0] <= -0.69115695f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[6] <= 0.24832809f) {
              if (x[0] <= 1.75225627f) {
                if (x[1] <= 0.10893319f) {
                  if (x[6] <= 0.11290298f) {
                    if (x[5] <= -1.10273761f) {
                      return 0.13178914f;
                    } else {
                      return 0.03621233f;
                    }
                  } else {
                    if (x[0] <= 0.77674910f) {
                      return 0.06359447f;
                    } else {
                      return 0.23145401f;
                    }
                  }
                } else {
                  if (x[0] <= -0.67567271f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[6] <= -1.88021231f) {
                      return 0.00000000f;
                    } else {
                      return 0.12140575f;
                    }
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[6] <= -2.21751654f) {
            if (x[0] <= 0.44538634f) {
              if (x[1] <= 5.33376575f) {
                return 0.00000000f;
              } else {
                if (x[7] <= 2.54726911f) {
                  return 0.54545455f;
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              if (x[0] <= 0.54293704f) {
                return 0.65000000f;
              } else {
                if (x[1] <= 0.76203725f) {
                  if (x[7] <= 3.65483510f) {
                    if (x[0] <= 1.48902422f) {
                      return 0.00000000f;
                    } else {
                      return 0.28571429f;
                    }
                  } else {
                    return 0.61538462f;
                  }
                } else {
                  if (x[1] <= 2.50364804f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= 2.93905067f) {
                      return 0.54545455f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[7] <= 9.20525122f) {
        if (x[4] <= 2.56777543f) {
          if (x[0] <= 1.33418179f) {
            if (x[7] <= 4.07017231f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[7] <= 4.35964990f) {
                if (x[0] <= 1.08953077f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  return 0.88888889f;
                }
              } else {
                if (x[6] <= -5.12739444f) {
                  if (x[6] <= -5.35394192f) {
                    if (x[3] <= 0.00074339f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    return 0.58823529f;
                  }
                } else {
                  if (x[5] <= 0.44373985f) {
                    if (x[6] <= -4.62395525f) {
                      return 0.96969697f;
                    } else {
                      return 0.58823529f;
                    }
                  } else {
                    if (x[5] <= 1.30645835f) {
                      return 0.96153846f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            }
          } else {
            if (x[7] <= 7.56907392f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[3] <= 0.00074339f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  }
}

static float rf_tree_091(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_092(const float* x) {
  if (x[6] <= 0.24832809f) {
    if (x[5] <= -0.85265636f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[1] <= -0.47015239f) {
        if (x[0] <= -0.67839792f) {
          if (x[5] <= 0.19935246f) {
            if (x[1] <= -0.94038731f) {
              if (x[1] <= -1.41062218f) {
                return 0.00000000f;
              } else {
                if (x[0] <= -0.68341485f) {
                  return 0.00000000f;
                } else {
                  if (x[7] <= -0.30974765f) {
                    return 0.05645161f;
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[1] <= -0.94038731f) {
              return 0.00520833f;
            } else {
              if (x[7] <= -0.31327173f) {
                if (x[1] <= -0.57900307f) {
                  if (x[3] <= -1.51086811f) {
                    return 0.45454545f;
                  } else {
                    if (x[0] <= -0.69115695f) {
                      return 0.07706592f;
                    } else {
                      return 0.26449275f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                return 0.00000000f;
              }
            }
          }
        } else {
          if (x[4] <= 2.56777543f) {
            if (x[6] <= 0.30068575f) {
              if (x[5] <= -1.27645630f) {
                if (x[5] <= -1.28126091f) {
                  if (x[6] <= 0.29162385f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= -1.38005859f) {
                      return 0.00000000f;
                    } else {
                      return 0.41176471f;
                    }
                  }
                } else {
                  return 0.61538462f;
                }
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[3] <= -1.51086811f) {
                return 0.00000000f;
              } else {
                if (x[7] <= -0.31327173f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            if (x[3] <= -1.51086811f) {
              if (x[5] <= 1.15445119f) {
                if (x[1] <= -0.76187220f) {
                  return 0.96774194f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 0.91666667f;
              }
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_093(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[1] <= -0.30228046f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_094(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_095(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[0] <= -0.68496326f) {
      if (x[3] <= 1.51235481f) {
        if (x[5] <= 0.19944394f) {
          if (x[6] <= 0.14361276f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[4] <= 2.56777543f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[6] <= 0.30974765f) {
                return 1.00000000f;
              } else {
                if (x[5] <= -1.29417229f) {
                  return 0.94736842f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        } else {
          if (x[5] <= 1.20122331f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            return 0.00148715f;
          }
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 0.63412052f) {
        if (x[6] <= 0.20053706f) {
          if (x[5] <= -1.13073641f) {
            if (x[6] <= -3.16700268f) {
              if (x[0] <= 1.27534163f) {
                return 0.00000000f;
              } else {
                if (x[7] <= 8.93238688f) {
                  if (x[1] <= 0.10893319f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[1] <= 0.54433589f) {
                      return 0.90000000f;
                    } else {
                      return 0.69230769f;
                    }
                  }
                } else {
                  return 0.86956522f;
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[0] <= -0.68186641f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[6] <= -5.31517720f) {
                if (x[5] <= 0.66905791f) {
                  return 0.02884615f;
                } else {
                  if (x[6] <= -7.64458966f) {
                    if (x[5] <= 0.91659704f) {
                      return 0.50000000f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[5] <= -1.41388869f) {
          return 0.80000000f;
        } else {
          if (x[7] <= 0.34472315f) {
            if (x[5] <= 1.40934539f) {
              if (x[3] <= -1.51086811f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[4] <= 2.56777543f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[4] <= 2.56777543f) {
              if (x[6] <= -2.50951111f) {
                if (x[7] <= 2.98777831f) {
                  if (x[7] <= 2.76123071f) {
                    if (x[5] <= -1.30882835f) {
                      return 0.80769231f;
                    } else {
                      return 0.93702771f;
                    }
                  } else {
                    if (x[5] <= 0.39794174f) {
                      return 0.98604651f;
                    } else {
                      return 0.93333333f;
                    }
                  }
                } else {
                  if (x[5] <= 1.40873212f) {
                    if (x[5] <= -1.41191578f) {
                      return 0.97752809f;
                    } else {
                      return 0.90918114f;
                    }
                  } else {
                    return 0.73333333f;
                  }
                }
              } else {
                if (x[7] <= 1.80469644f) {
                  if (x[3] <= 0.00074339f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[3] <= 0.00074339f) {
                    if (x[7] <= 1.88021231f) {
                      return 0.26086957f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            } else {
              if (x[5] <= -1.41381800f) {
                if (x[5] <= -1.41388166f) {
                  return 1.00000000f;
                } else {
                  return 0.89473684f;
                }
              } else {
                if (x[0] <= 1.52308953f) {
                  if (x[0] <= -0.61683258f) {
                    if (x[7] <= 0.79781833f) {
                      return 0.99537037f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  if (x[3] <= -4.53409100f) {
                    if (x[7] <= 1.02436590f) {
                      return 0.70967742f;
                    } else {
                      return 0.23636364f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

static float rf_tree_096(const float* x) {
  if (x[7] <= -0.30068575f) {
    if (x[3] <= 1.51235481f) {
      if (x[6] <= 0.32231183f) {
        return 0.00000000f;
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[0] <= -0.13991797f) {
            if (x[1] <= -1.41497624f) {
              return 0.98765432f;
            } else {
              if (x[5] <= 1.40307879f) {
                if (x[5] <= 0.74286827f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[0] <= -0.60444519f) {
                    if (x[0] <= -0.66947901f) {
                      return 0.99915326f;
                    } else {
                      return 0.99988359f;
                    }
                  } else {
                    if (x[3] <= -1.51086811f) {
                      return 0.94000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                if (x[1] <= -0.10876816f) {
                  return 0.99079190f;
                } else {
                  if (x[5] <= 1.40331006f) {
                    return 0.95652174f;
                  } else {
                    if (x[3] <= -1.51086811f) {
                      return 0.93333333f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            }
          } else {
            if (x[3] <= -4.53409100f) {
              if (x[0] <= 1.56799376f) {
                if (x[1] <= -0.10876816f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= -0.65632451f) {
                    return 0.00000000f;
                  } else {
                    return 0.42857143f;
                  }
                }
              } else {
                if (x[0] <= 1.72902989f) {
                  return 0.71428571f;
                } else {
                  if (x[5] <= 0.08945670f) {
                    return 0.00000000f;
                  } else {
                    return 0.73333333f;
                  }
                }
              }
            } else {
              return 1.00000000f;
            }
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_097(const float* x) {
  if (x[0] <= -0.68496326f) {
    if (x[1] <= -0.47015239f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 0.63412052f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_098(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[3] <= -7.55731416f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 2.56777543f) {
        if (x[0] <= -0.68496326f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[1] <= 0.30244550f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[0] <= 1.12049925f) {
              if (x[1] <= 0.47031744f) {
                if (x[0] <= -0.65399477f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[4] <= 0.63412052f) {
                    if (x[5] <= -1.20095295f) {
                      return 0.05248425f;
                    } else {
                      return 0.02361550f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      } else {
        if (x[1] <= -6.74865913f) {
          return 0.91666667f;
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_099(const float* x) {
  if (x[0] <= -0.68496326f) {
    if (x[5] <= 0.19746330f) {
      if (x[0] <= -0.69115695f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[4] <= 0.63412052f) {
          if (x[0] <= -0.68818396f) {
            if (x[6] <= 0.30974765f) {
              if (x[6] <= -2.58502710f) {
                return 0.20000000f;
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[5] <= -0.54679996f) {
                return 0.00000000f;
              } else {
                return 0.28571429f;
              }
            }
          } else {
            if (x[5] <= -0.63537732f) {
              return 0.00000000f;
            } else {
              return 0.01794454f;
            }
          }
        } else {
          if (x[5] <= -0.78859764f) {
            if (x[5] <= -0.79142019f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 0.60000000f;
            }
          } else {
            if (x[4] <= 2.56777543f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          }
        }
      }
    } else {
      if (x[1] <= -0.47015239f) {
        if (x[1] <= -0.94038731f) {
          if (x[5] <= 0.20192473f) {
            return 0.73684211f;
          } else {
            if (x[3] <= 1.51235481f) {
              if (x[5] <= 1.10940772f) {
                return 0.00000000f;
              } else {
                return 0.01496793f;
              }
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[1] <= 0.32663454f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[4] <= 2.56777543f) {
        if (x[1] <= -0.47015239f) {
          if (x[7] <= -0.30068575f) {
            if (x[3] <= -1.51086811f) {
              return 0.00000000f;
            } else {
              if (x[5] <= -1.41384268f) {
                if (x[1] <= -0.76187220f) {
                  return 0.00000000f;
                } else {
                  return 0.35714286f;
                }
              } else {
                if (x[7] <= -0.31381084f) {
                  if (x[5] <= -1.40937340f) {
                    if (x[1] <= -0.97957355f) {
                      return 0.00000000f;
                    } else {
                      return 0.04761905f;
                    }
                  } else {
                    return 0.00500935f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            if (x[1] <= -0.94038731f) {
              if (x[5] <= 1.36642212f) {
                if (x[5] <= -1.13872975f) {
                  if (x[6] <= 0.18388789f) {
                    return 0.00000000f;
                  } else {
                    if (x[6] <= 0.20503233f) {
                      return 0.73333333f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[7] <= 0.49575487f) {
                  if (x[5] <= 1.38150334f) {
                    if (x[1] <= -1.41497624f) {
                      return 0.00000000f;
                    } else {
                      return 0.69230769f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              if (x[6] <= -0.04265970f) {
                if (x[6] <= -0.51891306f) {
                  return 0.00000000f;
                } else {
                  if (x[7] <= 0.49575487f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= 0.39920613f) {
                      return 0.00000000f;
                    } else {
                      return 0.62500000f;
                    }
                  }
                }
              } else {
                if (x[7] <= 0.02604621f) {
                  if (x[6] <= 0.09125510f) {
                    if (x[5] <= 0.16997342f) {
                      return 0.00000000f;
                    } else {
                      return 0.09523810f;
                    }
                  } else {
                    if (x[6] <= 0.10031700f) {
                      return 0.25000000f;
                    } else {
                      return 0.07100592f;
                    }
                  }
                } else {
                  if (x[5] <= -0.81940806f) {
                    return 0.60000000f;
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            }
          }
        } else {
          if (x[6] <= 0.12196488f) {
            if (x[7] <= 4.08225489f) {
              if (x[7] <= 2.42694724f) {
                if (x[7] <= 0.95388445f) {
                  if (x[7] <= -0.11290298f) {
                    if (x[1] <= 0.10893319f) {
                      return 0.13238771f;
                    } else {
                      return 0.02061856f;
                    }
                  } else {
                    if (x[7] <= 0.61456648f) {
                      return 0.05424718f;
                    } else {
                      return 0.03415351f;
                    }
                  }
                } else {
                  if (x[1] <= 1.71750426f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[5] <= 0.99921846f) {
                      return 0.03787879f;
                    } else {
                      return 0.39743590f;
                    }
                  }
                }
              } else {
                if (x[1] <= -0.10876816f) {
                  if (x[6] <= -3.16398203f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= -0.32646950f) {
                      return 0.00000000f;
                    } else {
                      return 0.28358209f;
                    }
                  }
                } else {
                  if (x[7] <= 3.32407570f) {
                    if (x[6] <= -2.70132148f) {
                      return 0.00761697f;
                    } else {
                      return 0.03094463f;
                    }
                  } else {
                    if (x[7] <= 3.35478342f) {
                      return 0.17777778f;
                    } else {
                      return 0.04189189f;
                    }
                  }
                }
              }
            } else {
              if (x[5] <= -1.41203088f) {
                return 0.76666667f;
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[7] <= 0.92367807f) {
          if (x[6] <= 0.30974765f) {
            if (x[5] <= 1.40646338f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[0] <= -0.67257586f) {
                return 0.88000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[5] <= 0.23774800f) {
              if (x[1] <= 0.97973862f) {
                if (x[0] <= 0.71790898f) {
                  if (x[4] <= 14.16970444f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    return 0.96875000f;
                  }
                } else {
                  if (x[0] <= 0.73339322f) {
                    if (x[0] <= 0.73029637f) {
                      return 0.93750000f;
                    } else {
                      return 0.88888889f;
                    }
                  } else {
                    if (x[5] <= 0.10565711f) {
                      return 0.99668521f;
                    } else {
                      return 0.98753894f;
                    }
                  }
                }
              } else {
                if (x[0] <= -0.65554321f) {
                  return 0.90909091f;
                } else {
                  if (x[0] <= -0.64780107f) {
                    return 0.97959184f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            } else {
              if (x[3] <= -4.53409100f) {
                if (x[0] <= -0.63696212f) {
                  return 0.00000000f;
                } else {
                  return 0.57500000f;
                }
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[3] <= -4.53409100f) {
            if (x[0] <= 1.73522359f) {
              return 0.00000000f;
            } else {
              if (x[5] <= 1.07437778f) {
                if (x[7] <= 1.36418730f) {
                  return 0.47058824f;
                } else {
                  return 0.00000000f;
                }
              } else {
                return 0.77777778f;
              }
            }
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_100(const float* x) {
  if (x[6] <= 0.24832809f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[5] <= 1.04940593f) {
        if (x[1] <= 0.47031744f) {
          if (x[1] <= -0.47015239f) {
            if (x[4] <= 2.56777543f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[4] <= 2.56777543f) {
              if (x[6] <= 0.29162385f) {
                if (x[5] <= 0.24826612f) {
                  return 0.00000000f;
                } else {
                  if (x[0] <= -0.65089792f) {
                    if (x[7] <= -0.26997598f) {
                      return 0.07843137f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[4] <= 0.63412052f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[4] <= 2.56777543f) {
            if (x[7] <= -0.31327173f) {
              if (x[3] <= -1.51086811f) {
                return 0.00000000f;
              } else {
                if (x[1] <= 0.94055232f) {
                  if (x[5] <= -1.40403605f) {
                    return 0.03180212f;
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  if (x[5] <= -0.30276826f) {
                    if (x[1] <= 1.41078728f) {
                      return 0.00534147f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[3] <= -4.53409100f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_101(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_102(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_103(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_104(const float* x) {
  if (x[7] <= -0.24832809f) {
    if (x[3] <= 1.51235481f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_105(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[0] <= -0.67839792f) {
      if (x[5] <= -0.86384359f) {
        if (x[4] <= 0.63412052f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[3] <= 1.51235481f) {
          if (x[4] <= 2.56777543f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[6] <= -0.93223655f) {
        if (x[0] <= 0.98733479f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[4] <= 0.63412052f) {
            if (x[7] <= 1.69142264f) {
              if (x[6] <= -1.55297697f) {
                return 0.69230769f;
              } else {
                return 0.00000000f;
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[0] <= 1.20101732f) {
              if (x[7] <= 1.69142264f) {
                if (x[7] <= 1.06212384f) {
                  return 0.95454545f;
                } else {
                  return 0.92307692f;
                }
              } else {
                return 0.66666667f;
              }
            } else {
              if (x[7] <= 1.93055624f) {
                return 1.00000000f;
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        }
      } else {
        if (x[3] <= 1.51235481f) {
          if (x[4] <= 2.56777543f) {
            if (x[0] <= 0.83249235f) {
              if (x[0] <= -0.67567271f) {
                if (x[7] <= -0.22315614f) {
                  if (x[3] <= -1.51086811f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= -0.76187220f) {
                      return 0.00000000f;
                    } else {
                      return 0.13043478f;
                    }
                  }
                } else {
                  if (x[6] <= 0.10484795f) {
                    return 0.00000000f;
                  } else {
                    return 0.62500000f;
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          return 1.00000000f;
        }
      }
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_106(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_107(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[1] <= -0.47015239f) {
      if (x[0] <= -0.67839792f) {
        if (x[4] <= 2.56777543f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[0] <= 1.72748148f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[1] <= -0.73768315f) {
              return 0.00000000f;
            } else {
              if (x[5] <= -0.90799516f) {
                return 0.72222222f;
              } else {
                if (x[0] <= 1.74915946f) {
                  return 0.45454545f;
                } else {
                  return 0.00000000f;
                }
              }
            }
          }
        } else {
          if (x[1] <= -3.15658700f) {
            return 0.97777778f;
          } else {
            if (x[3] <= -1.51086811f) {
              if (x[6] <= -0.20627740f) {
                return 0.92857143f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          }
        }
      }
    } else {
      if (x[4] <= 2.56777543f) {
        if (x[6] <= -4.07319307f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[5] <= -1.17411023f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[6] <= 0.30068575f) {
              if (x[1] <= 0.30244550f) {
                if (x[1] <= 0.19359483f) {
                  if (x[6] <= 0.21761830f) {
                    if (x[0] <= -0.68496326f) {
                      return 0.00256674f;
                    } else {
                      return 0.04047635f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[6] <= -2.15710390f) {
                  if (x[0] <= 0.07686141f) {
                    return 0.00000000f;
                  } else {
                    if (x[6] <= -2.23261964f) {
                      return 0.05759162f;
                    } else {
                      return 0.76470588f;
                    }
                  }
                } else {
                  if (x[1] <= 0.73784819f) {
                    if (x[0] <= 1.29701960f) {
                      return 0.01313869f;
                    } else {
                      return 0.05882353f;
                    }
                  } else {
                    if (x[7] <= 1.22825873f) {
                      return 0.00000000f;
                    } else {
                      return 0.01272265f;
                    }
                  }
                }
              }
            } else {
              if (x[0] <= -0.60444519f) {
                if (x[1] <= 0.32663454f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        }
      } else {
        if (x[0] <= 1.44257146f) {
          if (x[6] <= -0.47058292f) {
            if (x[6] <= -0.52092680f) {
              if (x[3] <= -4.53409100f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[6] <= -0.49575487f) {
                return 0.96774194f;
              } else {
                return 0.94594595f;
              }
            }
          } else {
            if (x[3] <= -4.53409100f) {
              if (x[3] <= -7.55731416f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[4] <= 5.46825778f) {
                  if (x[6] <= 0.03285616f) {
                    return 0.72727273f;
                  } else {
                    if (x[7] <= -0.30974765f) {
                      return 0.25842697f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[3] <= -4.53409100f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            return 1.00000000f;
          }
        }
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_108(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[0] <= -0.64780107f) {
      if (x[3] <= -1.51086811f) {
        if (x[0] <= -0.70664120f) {
          if (x[7] <= -0.30974765f) {
            if (x[4] <= 4.50143015f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            return 0.00000000f;
          }
        } else {
          if (x[4] <= 4.50143015f) {
            if (x[6] <= -0.74747440f) {
              if (x[7] <= 0.83557624f) {
                return 0.61538462f;
              } else {
                if (x[7] <= 2.05641592f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= -0.98682272f) {
                    return 0.62500000f;
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[0] <= -0.65089792f) {
              return 0.99870634f;
            } else {
              if (x[5] <= -1.10203987f) {
                if (x[5] <= -1.16284049f) {
                  return 1.00000000f;
                } else {
                  return 0.78947368f;
                }
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[5] <= -1.37018305f) {
        if (x[5] <= -1.37354398f) {
          if (x[1] <= 0.30244550f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[4] <= 2.56777543f) {
              if (x[0] <= 1.71664250f) {
                if (x[3] <= 0.00074339f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[5] <= -1.38779730f) {
                  return 0.00000000f;
                } else {
                  return 0.50000000f;
                }
              }
            } else {
              if (x[5] <= -1.41219264f) {
                return 1.00000000f;
              } else {
                if (x[7] <= -0.30974765f) {
                  if (x[0] <= -0.63851053f) {
                    return 0.98245614f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        } else {
          if (x[4] <= 2.56777543f) {
            if (x[6] <= -0.63420062f) {
              return 0.92682927f;
            } else {
              if (x[5] <= -1.37179202f) {
                return 0.80281690f;
              } else {
                if (x[3] <= 0.00074339f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[0] <= 1.35276282f) {
            if (x[6] <= -3.96948445f) {
              if (x[3] <= 0.00074339f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[0] <= 1.29082590f) {
                if (x[0] <= 1.21030784f) {
                  if (x[3] <= 0.00074339f) {
                    if (x[0] <= -0.45579650f) {
                      return 0.00000000f;
                    } else {
                      return 0.01334816f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[6] <= -1.33901531f) {
                  if (x[3] <= 0.00074339f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[3] <= 0.00074339f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            }
          } else {
            if (x[0] <= 1.41160297f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[3] <= 0.00074339f) {
                if (x[5] <= 0.33388375f) {
                  if (x[1] <= -0.19342980f) {
                    if (x[5] <= -0.95128709f) {
                      return 0.06122449f;
                    } else {
                      return 0.35294118f;
                    }
                  } else {
                    if (x[7] <= -0.30974765f) {
                      return 0.04816514f;
                    } else {
                      return 0.08590308f;
                    }
                  }
                } else {
                  if (x[6] <= 0.30974765f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= 1.08553028f) {
                      return 0.00000000f;
                    } else {
                      return 0.02604167f;
                    }
                  }
                }
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    }
  }
}

static float rf_tree_109(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[1] <= -3.15658700f) {
      if (x[3] <= -1.51086811f) {
        if (x[6] <= -0.35730911f) {
          return 0.68750000f;
        } else {
          return 0.00000000f;
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[1] <= -1.41497624f) {
        if (x[0] <= 0.30293132f) {
          if (x[6] <= -0.78523234f) {
            if (x[6] <= -1.70400864f) {
              return 1.00000000f;
            } else {
              return 0.94736842f;
            }
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[3] <= -1.51086811f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[3] <= -1.51086811f) {
          if (x[3] <= -7.55731416f) {
            if (x[0] <= -0.64780107f) {
              return 0.35294118f;
            } else {
              if (x[0] <= 1.72902989f) {
                if (x[5] <= -0.79943794f) {
                  return 1.00000000f;
                } else {
                  return 0.86363636f;
                }
              } else {
                if (x[4] <= 8.36874008f) {
                  return 0.43750000f;
                } else {
                  return 0.89473684f;
                }
              }
            }
          } else {
            if (x[6] <= -0.29437923f) {
              if (x[4] <= 4.50143015f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[1] <= 0.10893319f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[4] <= 4.50143015f) {
                  if (x[1] <= 0.54433589f) {
                    if (x[5] <= 0.22228347f) {
                      return 0.01492537f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        } else {
          return 1.00000000f;
        }
      }
    }
  }
}

static float rf_tree_110(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_111(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[0] <= -0.68496326f) {
        if (x[1] <= 0.32663454f) {
          if (x[4] <= 2.56777543f) {
            if (x[7] <= 2.63537097f) {
              if (x[6] <= -0.21886338f) {
                return 0.00000000f;
              } else {
                if (x[7] <= 0.19570518f) {
                  if (x[1] <= -0.32646950f) {
                    return 0.00000000f;
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  if (x[0] <= -0.73915806f) {
                    return 0.66666667f;
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            } else {
              if (x[7] <= 2.68571484f) {
                return 0.40000000f;
              } else {
                return 0.00000000f;
              }
            }
          } else {
            if (x[1] <= -0.10876816f) {
              return 1.00000000f;
            } else {
              if (x[0] <= -0.71902859f) {
                return 1.00000000f;
              } else {
                if (x[4] <= 4.50143015f) {
                  return 0.99834711f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        } else {
          if (x[3] <= -1.51086811f) {
            return 0.28846154f;
          } else {
            if (x[7] <= -0.31327173f) {
              if (x[0] <= -0.79644978f) {
                return 0.00000000f;
              } else {
                if (x[1] <= 0.47031744f) {
                  if (x[4] <= 1.60094798f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[5] <= 0.93028998f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            } else {
              if (x[0] <= -0.73296437f) {
                if (x[7] <= 0.19369143f) {
                  return 0.00000000f;
                } else {
                  return 0.15151515f;
                }
              } else {
                return 0.00000000f;
              }
            }
          }
        }
      } else {
        if (x[0] <= -0.68186641f) {
          if (x[4] <= 2.56777543f) {
            if (x[5] <= -0.87436968f) {
              return 0.80000000f;
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[7] <= -0.30068575f) {
            if (x[5] <= 1.27322614f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[1] <= 0.76203725f) {
                if (x[4] <= 2.56777543f) {
                  if (x[0] <= -0.67325717f) {
                    if (x[4] <= 0.63412052f) {
                      return 0.15654952f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  if (x[0] <= -0.61683258f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[3] <= -1.51086811f) {
                      return 0.98058252f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                if (x[0] <= -0.10894949f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[0] <= 0.12641098f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    return 0.16304348f;
                  }
                }
              }
            }
          } else {
            if (x[4] <= 2.56777543f) {
              if (x[5] <= -1.24154729f) {
                if (x[6] <= 0.04795934f) {
                  if (x[1] <= 0.32663454f) {
                    if (x[7] <= 8.29906082f) {
                      return 0.14773473f;
                    } else {
                      return 0.61290323f;
                    }
                  } else {
                    if (x[4] <= 0.63412052f) {
                      return 0.04874446f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[4] <= 10.30239487f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 0.95238095f;
              }
            }
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_112(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_113(const float* x) {
  if (x[0] <= -0.67839792f) {
    if (x[0] <= -0.69115695f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[5] <= -0.87650979f) {
        if (x[0] <= -0.68806010f) {
          if (x[5] <= -1.31371421f) {
            return 0.73333333f;
          } else {
            return 0.50000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  } else {
    if (x[1] <= 0.84669888f) {
      if (x[1] <= -0.84653383f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[4] <= 0.63412052f) {
          if (x[1] <= 0.30244550f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[0] <= -0.60444519f) {
              if (x[1] <= 0.47031744f) {
                if (x[5] <= -1.41387945f) {
                  return 0.40000000f;
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[6] <= 0.13354398f) {
                  if (x[0] <= -0.67325717f) {
                    return 0.54545455f;
                  } else {
                    if (x[5] <= -0.68395147f) {
                      return 0.03164557f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  if (x[1] <= 0.57916811f) {
                    return 0.00000000f;
                  } else {
                    if (x[0] <= -0.66328532f) {
                      return 0.00000000f;
                    } else {
                      return 0.01085645f;
                    }
                  }
                }
              }
            } else {
              if (x[6] <= -3.71776497f) {
                if (x[0] <= 1.17004883f) {
                  return 0.00000000f;
                } else {
                  if (x[0] <= 1.56180012f) {
                    return 0.88235294f;
                  } else {
                    if (x[6] <= -4.82533097f) {
                      return 0.00000000f;
                    } else {
                      return 0.36363636f;
                    }
                  }
                }
              } else {
                if (x[5] <= 1.33214492f) {
                  if (x[0] <= -0.59515464f) {
                    if (x[7] <= 0.65937258f) {
                      return 0.04977376f;
                    } else {
                      return 0.46666667f;
                    }
                  } else {
                    if (x[6] <= 0.29162385f) {
                      return 0.01265823f;
                    } else {
                      return 0.03042715f;
                    }
                  }
                } else {
                  if (x[7] <= -0.15871593f) {
                    if (x[1] <= 0.54433589f) {
                      return 0.04819277f;
                    } else {
                      return 0.11111111f;
                    }
                  } else {
                    if (x[5] <= 1.37158823f) {
                      return 0.68000000f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              }
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[3] <= 1.51235481f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_114(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[3] <= -7.55731416f) {
      if (x[6] <= -0.59644267f) {
        return 0.96153846f;
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_115(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_116(const float* x) {
  if (x[0] <= -0.67839792f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_117(const float* x) {
  if (x[6] <= -0.80587333f) {
    if (x[1] <= -0.47015239f) {
      if (x[3] <= 1.51235481f) {
        if (x[4] <= 2.56777543f) {
          if (x[0] <= 1.36378759f) {
            return 0.00000000f;
          } else {
            if (x[0] <= 1.38218290f) {
              return 0.54545455f;
            } else {
              return 0.00000000f;
            }
          }
        } else {
          if (x[7] <= 2.67312884f) {
            if (x[5] <= -1.25307059f) {
              if (x[0] <= -0.45115121f) {
                return 1.00000000f;
              } else {
                return 0.93333333f;
              }
            } else {
              if (x[0] <= 1.11895078f) {
                return 1.00000000f;
              } else {
                return 0.95833333f;
              }
            }
          } else {
            return 1.00000000f;
          }
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[4] <= 0.63412052f) {
      if (x[0] <= -0.68496326f) {
        if (x[7] <= 0.21382899f) {
          if (x[6] <= -0.20476709f) {
            if (x[0] <= -0.74070650f) {
              if (x[5] <= 0.70079964f) {
                return 0.00000000f;
              } else {
                return 0.75000000f;
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[1] <= -0.32646950f) {
              return 0.00000000f;
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          return 0.00000000f;
        }
      } else {
        if (x[0] <= -0.68186641f) {
          if (x[7] <= -0.20905984f) {
            if (x[1] <= 0.10893319f) {
              if (x[1] <= -0.32646950f) {
                return 0.00000000f;
              } else {
                if (x[1] <= -0.10876816f) {
                  return 0.20512821f;
                } else {
                  return 0.10204082f;
                }
              }
            } else {
              return 0.28571429f;
            }
          } else {
            if (x[6] <= -0.42023900f) {
              return 0.00000000f;
            } else {
              return 0.69565217f;
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[1] <= 7.40192819f) {
        if (x[4] <= 2.56777543f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[3] <= -4.53409100f) {
            if (x[4] <= 4.50143015f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[6] <= 0.30974765f) {
                if (x[7] <= -0.05802812f) {
                  return 0.66666667f;
                } else {
                  return 0.92857143f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            return 1.00000000f;
          }
        }
      } else {
        return 0.50000000f;
      }
    }
  }
}

static float rf_tree_118(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_119(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_120(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_121(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[7] <= -0.24832809f) {
      if (x[0] <= -0.67839792f) {
        if (x[4] <= 2.56777543f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[3] <= -4.53409100f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[0] <= -0.67325717f) {
          if (x[4] <= 2.56777543f) {
            if (x[7] <= -0.31327173f) {
              if (x[5] <= 1.40573281f) {
                if (x[3] <= -1.51086811f) {
                  return 0.00000000f;
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[3] <= -1.51086811f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= 1.40909851f) {
                    if (x[0] <= -0.67567271f) {
                      return 0.85294118f;
                    } else {
                      return 0.52631579f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            } else {
              return 0.06451613f;
            }
          } else {
            if (x[7] <= -0.30974765f) {
              if (x[4] <= 4.50143015f) {
                if (x[1] <= -0.10876816f) {
                  return 1.00000000f;
                } else {
                  if (x[0] <= -0.67567271f) {
                    return 0.98630137f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                return 1.00000000f;
              }
            } else {
              return 0.98113208f;
            }
          }
        } else {
          if (x[1] <= 0.47031744f) {
            if (x[4] <= 2.56777543f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[0] <= 0.00253705f) {
                if (x[3] <= -4.53409100f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[4] <= 8.36874008f) {
                  if (x[3] <= -4.53409100f) {
                    return 0.28750000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  return 0.96666667f;
                }
              }
            }
          } else {
            if (x[4] <= 2.56777543f) {
              if (x[7] <= -0.31327173f) {
                if (x[1] <= 0.73784819f) {
                  if (x[0] <= -0.66328532f) {
                    return 0.00000000f;
                  } else {
                    if (x[0] <= -0.65164116f) {
                      return 0.12222222f;
                    } else {
                      return 0.01220753f;
                    }
                  }
                } else {
                  if (x[5] <= -1.41016185f) {
                    if (x[1] <= 0.97973862f) {
                      return 0.08771930f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[3] <= -4.53409100f) {
                return 0.41666667f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      }
    } else {
      if (x[6] <= -0.93223655f) {
        if (x[3] <= -1.51086811f) {
          if (x[0] <= 1.58347803f) {
            if (x[6] <= -4.53585339f) {
              if (x[4] <= 3.53460270f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[5] <= -1.24064022f) {
              if (x[4] <= 4.50143015f) {
                if (x[7] <= 0.99919394f) {
                  return 0.61538462f;
                } else {
                  if (x[5] <= -1.24701935f) {
                    if (x[7] <= 1.50263304f) {
                      return 0.22916667f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.70000000f;
                  }
                }
              } else {
                if (x[0] <= 1.76120275f) {
                  return 1.00000000f;
                } else {
                  return 0.96363636f;
                }
              }
            } else {
              if (x[7] <= 6.99011898f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 0.00000000f;
              }
            }
          }
        } else {
          if (x[0] <= -0.68496326f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[5] <= -0.84442055f) {
              if (x[4] <= 1.60094798f) {
                if (x[5] <= -0.85095429f) {
                  if (x[5] <= -1.16056734f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  if (x[0] <= 0.80926603f) {
                    if (x[5] <= -0.84900713f) {
                      return 0.71428571f;
                    } else {
                      return 0.66666667f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[0] <= -0.68496326f) {
            if (x[0] <= -0.74070650f) {
              if (x[6] <= -0.19369143f) {
                if (x[0] <= -0.74690020f) {
                  return 0.00000000f;
                } else {
                  if (x[1] <= 0.32663454f) {
                    if (x[6] <= -0.21886338f) {
                      return 0.00000000f;
                    } else {
                      return 0.81818182f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                return 0.00000000f;
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_122(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_123(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[7] <= -0.24832809f) {
      if (x[1] <= -0.47015239f) {
        if (x[7] <= -0.30068575f) {
          if (x[3] <= -1.51086811f) {
            if (x[5] <= -0.45469978f) {
              if (x[1] <= -1.19727486f) {
                return 0.00000000f;
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[4] <= 1.60094798f) {
              if (x[7] <= -0.31327173f) {
                return 0.00569023f;
              } else {
                return 0.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[0] <= -0.66793057f) {
            return 0.00000000f;
          } else {
            if (x[1] <= -0.94038731f) {
              if (x[1] <= -1.41062218f) {
                return 0.00000000f;
              } else {
                if (x[4] <= 0.63412052f) {
                  return 0.00000000f;
                } else {
                  return 0.92307692f;
                }
              }
            } else {
              if (x[4] <= 2.56777543f) {
                if (x[5] <= -1.36547559f) {
                  if (x[5] <= -1.39749652f) {
                    return 0.00000000f;
                  } else {
                    return 0.81250000f;
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_124(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_125(const float* x) {
  if (x[0] <= -0.67839792f) {
    if (x[0] <= -0.69115695f) {
      if (x[3] <= 1.51235481f) {
        if (x[5] <= 0.19928332f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 0.63412052f) {
        if (x[6] <= -4.33447766f) {
          if (x[0] <= -0.68341485f) {
            return 0.00000000f;
          } else {
            if (x[5] <= 1.27273554f) {
              return 0.00000000f;
            } else {
              return 0.61538462f;
            }
          }
        } else {
          if (x[5] <= 1.13728517f) {
            if (x[6] <= 0.23423179f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[5] <= 1.10463953f) {
                if (x[5] <= -0.48091964f) {
                  if (x[0] <= -0.68496326f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= -0.57578111f) {
                      return 0.01190476f;
                    } else {
                      return 0.24305556f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            return 0.00000000f;
          }
        }
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[5] <= 1.40344816f) {
            if (x[1] <= -0.10876816f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[6] <= -2.73605871f) {
                return 0.70588235f;
              } else {
                if (x[3] <= 0.00074339f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            return 0.58823529f;
          }
        } else {
          if (x[4] <= 4.50143015f) {
            if (x[6] <= -1.07470977f) {
              return 1.00000000f;
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            return 1.00000000f;
          }
        }
      }
    }
  } else {
    if (x[0] <= -0.67325717f) {
      if (x[4] <= 0.63412052f) {
        if (x[0] <= -0.67567271f) {
          if (x[5] <= 1.39684254f) {
            if (x[6] <= 0.28457570f) {
              if (x[5] <= -0.51148090f) {
                return 0.33333333f;
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[7] <= -0.30068575f) {
                if (x[5] <= -1.19029826f) {
                  if (x[5] <= -1.31785178f) {
                    return 0.00000000f;
                  } else {
                    return 0.75000000f;
                  }
                } else {
                  if (x[1] <= -0.10876816f) {
                    return 0.16981132f;
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                return 0.33333333f;
              }
            }
          } else {
            if (x[1] <= 0.10893319f) {
              if (x[6] <= 0.12095800f) {
                return 0.00000000f;
              } else {
                if (x[5] <= 1.40702528f) {
                  return 0.18750000f;
                } else {
                  if (x[1] <= -0.10876816f) {
                    return 0.79310345f;
                  } else {
                    return 0.33333333f;
                  }
                }
              }
            } else {
              return 0.61538462f;
            }
          }
        } else {
          if (x[7] <= 0.20627740f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[1] <= 0.10893319f) {
              if (x[6] <= -0.57127070f) {
                return 0.00000000f;
              } else {
                return 0.50000000f;
              }
            } else {
              if (x[7] <= 0.52092682f) {
                return 0.95652174f;
              } else {
                return 0.30000000f;
              }
            }
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[4] <= 0.63412052f) {
        if (x[0] <= 1.05856228f) {
          if (x[0] <= -0.65678194f) {
            if (x[6] <= 0.30068575f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[1] <= -0.32646950f) {
                if (x[0] <= -0.66328532f) {
                  if (x[0] <= -0.66947901f) {
                    if (x[5] <= 1.28935117f) {
                      return 0.00231125f;
                    } else {
                      return 0.05194805f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[5] <= -1.31232524f) {
                    if (x[5] <= -1.31375861f) {
                      return 0.01526718f;
                    } else {
                      return 0.78571429f;
                    }
                  } else {
                    return 0.00258665f;
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[0] <= -0.65164116f) {
              if (x[5] <= -1.15215558f) {
                if (x[7] <= 0.34472314f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[0] <= -0.64780107f) {
                if (x[0] <= -0.65009275f) {
                  return 0.00000000f;
                } else {
                  if (x[6] <= -6.90201712f) {
                    if (x[1] <= 0.10893319f) {
                      return 0.00000000f;
                    } else {
                      return 0.66666667f;
                    }
                  } else {
                    if (x[1] <= 0.54433589f) {
                      return 0.01648255f;
                    } else {
                      return 0.00263296f;
                    }
                  }
                }
              } else {
                if (x[6] <= -1.18496299f) {
                  if (x[7] <= 1.19402486f) {
                    if (x[1] <= 0.32663454f) {
                      return 0.00000000f;
                    } else {
                      return 0.46153846f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  if (x[5] <= -1.12088120f) {
                    if (x[1] <= 0.76203725f) {
                      return 0.04905361f;
                    } else {
                      return 0.00739372f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            }
          }
        } else {
          if (x[5] <= -0.83536780f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[6] <= -5.35847306f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[5] <= 1.10347891f) {
                if (x[5] <= 1.03416717f) {
                  if (x[7] <= 4.08225298f) {
                    if (x[6] <= -2.37458944f) {
                      return 0.02534319f;
                    } else {
                      return 0.04477700f;
                    }
                  } else {
                    if (x[5] <= 0.98575369f) {
                      return 0.05392157f;
                    } else {
                      return 0.72222222f;
                    }
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  }
}

static float rf_tree_126(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[3] <= 1.51235481f) {
      if (x[6] <= -1.02436590f) {
        if (x[5] <= -1.41283375f) {
          return 0.94736842f;
        } else {
          if (x[0] <= -0.23282342f) {
            if (x[5] <= -0.08837678f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[1] <= -0.76187220f) {
                if (x[0] <= -0.64160737f) {
                  return 0.00000000f;
                } else {
                  if (x[6] <= -2.00607216f) {
                    return 0.00000000f;
                  } else {
                    if (x[0] <= -0.63386527f) {
                      return 0.38461538f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              } else {
                if (x[4] <= 2.56777543f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[7] <= 9.23042297f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[7] <= 9.78420591f) {
                return 0.94736842f;
              } else {
                if (x[0] <= 0.26422071f) {
                  return 0.71428571f;
                } else {
                  return 0.00000000f;
                }
              }
            }
          }
        }
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[6] <= 0.24832809f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[0] <= 1.72748148f) {
              if (x[6] <= 0.30068575f) {
                if (x[5] <= -1.36856753f) {
                  if (x[0] <= -0.65399477f) {
                    if (x[5] <= -1.38913709f) {
                      return 0.00000000f;
                    } else {
                      return 0.77777778f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[0] <= 1.73832047f) {
                if (x[5] <= 0.06680503f) {
                  return 0.46666667f;
                } else {
                  return 0.72727273f;
                }
              } else {
                return 0.00000000f;
              }
            }
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[6] <= -0.80587333f) {
      if (x[1] <= 0.73784819f) {
        if (x[0] <= -0.69115695f) {
          if (x[5] <= 1.40224373f) {
            return 0.00000000f;
          } else {
            return 0.50000000f;
          }
        } else {
          if (x[5] <= -0.84321579f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[3] <= 1.51235481f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[4] <= 0.63412052f) {
        if (x[1] <= 0.30244550f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[1] <= 4.35410953f) {
          if (x[5] <= -1.35826373f) {
            if (x[6] <= 0.23423179f) {
              if (x[3] <= -1.51086811f) {
                if (x[3] <= -4.53409100f) {
                  return 0.50000000f;
                } else {
                  if (x[6] <= -0.29437923f) {
                    return 0.29032258f;
                  } else {
                    if (x[5] <= -1.37549835f) {
                      return 0.04901961f;
                    } else {
                      return 0.62500000f;
                    }
                  }
                }
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[0] <= -0.71902859f) {
              if (x[6] <= -0.19369143f) {
                if (x[5] <= 0.69524005f) {
                  return 0.97500000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[7] <= -0.20905983f) {
                  if (x[3] <= -1.51086811f) {
                    if (x[0] <= -0.75619075f) {
                      return 0.53846154f;
                    } else {
                      return 0.08695652f;
                    }
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  return 0.85000000f;
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          return 0.73076923f;
        }
      }
    }
  }
}

static float rf_tree_127(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_128(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[7] <= -0.24832809f) {
      if (x[0] <= -0.67839792f) {
        if (x[0] <= -0.72831911f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[1] <= 0.47031744f) {
          if (x[7] <= -0.26997598f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            return 0.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[0] <= -0.68496326f) {
        if (x[4] <= 2.56777543f) {
          if (x[1] <= 0.10893319f) {
            if (x[4] <= 0.63412052f) {
              if (x[7] <= 2.63537097f) {
                return 0.00000000f;
              } else {
                if (x[5] <= 0.94860578f) {
                  return 0.00000000f;
                } else {
                  return 0.07594937f;
                }
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[1] <= 0.32663454f) {
              if (x[5] <= 0.69584230f) {
                return 0.00000000f;
              } else {
                return 0.85714286f;
              }
            } else {
              return 0.00000000f;
            }
          }
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[5] <= -0.85718623f) {
          if (x[5] <= -0.96204978f) {
            if (x[0] <= 0.51351699f) {
              if (x[1] <= 0.54433589f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[5] <= -1.41367161f) {
                  return 0.86363636f;
                } else {
                  if (x[0] <= 0.42061155f) {
                    if (x[5] <= -1.09970081f) {
                      return 0.04116638f;
                    } else {
                      return 0.12244898f;
                    }
                  } else {
                    return 0.63636364f;
                  }
                }
              }
            } else {
              if (x[1] <= 0.19359483f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[1] <= -0.54417084f) {
              if (x[5] <= -0.89366955f) {
                if (x[4] <= 0.63412052f) {
                  return 0.00000000f;
                } else {
                  return 0.89473684f;
                }
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[1] <= -0.94038731f) {
            if (x[0] <= -0.53786296f) {
              if (x[4] <= 1.60094798f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[0] <= 0.29673763f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[1] <= 0.32663454f) {
              if (x[1] <= 0.19359483f) {
                if (x[6] <= 0.01724955f) {
                  if (x[6] <= -6.05875659f) {
                    if (x[4] <= 2.56777543f) {
                      return 0.12941176f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[4] <= 2.56777543f) {
                      return 0.04048745f;
                    } else {
                      return 0.99379475f;
                    }
                  }
                } else {
                  if (x[1] <= -0.32646950f) {
                    if (x[5] <= 0.78429911f) {
                      return 0.23952096f;
                    } else {
                      return 0.47512438f;
                    }
                  } else {
                    if (x[5] <= 0.11504689f) {
                      return 0.35943517f;
                    } else {
                      return 0.52486834f;
                    }
                  }
                }
              } else {
                if (x[0] <= 0.37415883f) {
                  if (x[6] <= -2.73605883f) {
                    if (x[4] <= 2.56777543f) {
                      return 0.14457831f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[4] <= 2.56777543f) {
                      return 0.11153119f;
                    } else {
                      return 0.99811853f;
                    }
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_129(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[0] <= -0.68496326f) {
      if (x[0] <= -0.72831911f) {
        if (x[6] <= -0.20476709f) {
          if (x[5] <= 0.69741023f) {
            return 0.00000000f;
          } else {
            if (x[1] <= 0.10893319f) {
              return 0.00000000f;
            } else {
              if (x[6] <= -0.26920728f) {
                return 0.00000000f;
              } else {
                return 0.80000000f;
              }
            }
          }
        } else {
          if (x[1] <= -0.10876816f) {
            if (x[5] <= 0.68362576f) {
              return 0.00000000f;
            } else {
              if (x[5] <= 0.69209656f) {
                return 0.20000000f;
              } else {
                return 0.00000000f;
              }
            }
          } else {
            return 0.00000000f;
          }
        }
      } else {
        if (x[7] <= -0.31327173f) {
          if (x[5] <= -0.31341444f) {
            return 0.00075443f;
          } else {
            if (x[0] <= -0.72522229f) {
              if (x[5] <= 0.26819642f) {
                if (x[5] <= 0.25069652f) {
                  return 0.75000000f;
                } else {
                  return 0.62500000f;
                }
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[1] <= -0.32646950f) {
                return 0.00000000f;
              } else {
                if (x[1] <= 0.32663454f) {
                  if (x[0] <= -0.71902859f) {
                    return 0.00000000f;
                  } else {
                    if (x[1] <= 0.10893319f) {
                      return 0.03127299f;
                    } else {
                      return 0.10593220f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              }
            }
          }
        } else {
          if (x[7] <= 2.63537097f) {
            return 0.00000000f;
          } else {
            if (x[0] <= -0.69115695f) {
              return 0.00000000f;
            } else {
              if (x[7] <= 2.76123071f) {
                if (x[5] <= 0.80709571f) {
                  return 0.00000000f;
                } else {
                  return 0.61538462f;
                }
              } else {
                return 0.00000000f;
              }
            }
          }
        }
      }
    } else {
      if (x[1] <= 0.30244550f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[1] <= 0.47031744f) {
          if (x[6] <= -3.70517898f) {
            return 0.18888889f;
          } else {
            if (x[5] <= -1.41387725f) {
              return 0.41176471f;
            } else {
              if (x[5] <= 1.37996721f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 0.00000000f;
              }
            }
          }
        } else {
          if (x[0] <= 1.75380468f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[0] <= 1.76774049f) {
              if (x[7] <= 1.80822057f) {
                if (x[1] <= 1.19743997f) {
                  return 0.00000000f;
                } else {
                  return 0.36363636f;
                }
              } else {
                return 0.70000000f;
              }
            } else {
              return 0.00000000f;
            }
          }
        }
      }
    }
  } else {
    if (x[3] <= -1.51086811f) {
      if (x[7] <= 0.29437923f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[0] <= -0.13372427f) {
          if (x[0] <= -0.65089792f) {
            if (x[7] <= 0.62161463f) {
              if (x[4] <= 2.56777543f) {
                return 0.00000000f;
              } else {
                return 0.55555556f;
              }
            } else {
              if (x[5] <= 1.09780526f) {
                if (x[4] <= 4.50143015f) {
                  if (x[7] <= 0.77264637f) {
                    if (x[7] <= 0.69713050f) {
                      return 0.00000000f;
                    } else {
                      return 0.70000000f;
                    }
                  } else {
                    if (x[0] <= -0.65709162f) {
                      return 0.00000000f;
                    } else {
                      return 0.30000000f;
                    }
                  }
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[4] <= 3.53460270f) {
                  return 0.00000000f;
                } else {
                  return 0.92857143f;
                }
              }
            }
          } else {
            if (x[4] <= 4.50143015f) {
              if (x[5] <= -1.04001826f) {
                return 0.16666667f;
              } else {
                return 0.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[6] <= -1.17539763f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[5] <= 0.48482738f) {
              if (x[4] <= 4.50143015f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[6] <= -0.89850610f) {
                  return 0.96491228f;
                } else {
                  if (x[6] <= -0.53351280f) {
                    return 1.00000000f;
                  } else {
                    if (x[5] <= -1.34909105f) {
                      return 0.95454545f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_130(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[0] <= -0.68496326f) {
      if (x[5] <= 0.24399964f) {
        if (x[0] <= -0.71902859f) {
          return 0.00000000f;
        } else {
          if (x[0] <= -0.71648917f) {
            if (x[5] <= -1.22170848f) {
              if (x[1] <= -0.10876816f) {
                return 0.38461538f;
              } else {
                return 0.00000000f;
              }
            } else {
              return 0.00000000f;
            }
          } else {
            return 0.00234192f;
          }
        }
      } else {
        if (x[5] <= 0.24437692f) {
          return 0.53846154f;
        } else {
          if (x[5] <= 1.13710362f) {
            if (x[7] <= 2.63537097f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[5] <= 0.95057967f) {
                return 0.00000000f;
              } else {
                if (x[1] <= -0.21761883f) {
                  return 0.66666667f;
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            return 0.00000000f;
          }
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[4] <= 2.56777543f) {
      if (x[6] <= 0.23423179f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[5] <= 1.40357494f) {
          if (x[3] <= 0.00074339f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[3] <= 0.00074339f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[3] <= -4.53409100f) {
        if (x[0] <= -0.65089792f) {
          if (x[5] <= -1.38342422f) {
            return 0.50000000f;
          } else {
            return 0.00000000f;
          }
        } else {
          if (x[3] <= -7.55731416f) {
            if (x[0] <= 1.60825288f) {
              if (x[5] <= -0.70501399f) {
                if (x[5] <= -1.21708667f) {
                  return 0.94736842f;
                } else {
                  return 0.78571429f;
                }
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[0] <= 1.72902989f) {
                return 0.82352941f;
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_131(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_132(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_133(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_134(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_135(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_136(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[6] <= -4.08225489f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[1] <= -3.15658700f) {
      if (x[5] <= 0.61487520f) {
        if (x[4] <= 2.56777543f) {
          if (x[5] <= -1.10741717f) {
            return 0.82608696f;
          } else {
            if (x[0] <= 0.33080296f) {
              return 0.80000000f;
            } else {
              return 0.42857143f;
            }
          }
        } else {
          if (x[0] <= 0.39893362f) {
            return 0.95238095f;
          } else {
            return 1.00000000f;
          }
        }
      } else {
        if (x[5] <= 1.30255920f) {
          return 1.00000000f;
        } else {
          return 0.92307692f;
        }
      }
    } else {
      if (x[3] <= -1.51086811f) {
        if (x[4] <= 4.50143015f) {
          if (x[0] <= 1.37134397f) {
            if (x[4] <= 2.56777543f) {
              if (x[6] <= -0.47058292f) {
                if (x[0] <= -0.12598215f) {
                  if (x[5] <= -1.03888381f) {
                    if (x[0] <= -0.26998560f) {
                      return 0.15254237f;
                    } else {
                      return 0.64000000f;
                    }
                  } else {
                    if (x[7] <= 0.77264637f) {
                      return 0.11111111f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[5] <= 0.21725280f) {
                  return 0.00000000f;
                } else {
                  if (x[5] <= 0.21990971f) {
                    return 0.50000000f;
                  } else {
                    return 0.00000000f;
                  }
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          } else {
            if (x[0] <= 1.37753761f) {
              return 0.50000000f;
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[1] <= -0.10876816f) {
            return 1.00000000f;
          } else {
            if (x[4] <= 15.13653183f) {
              if (x[3] <= -7.55731416f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 1.00000000f;
              }
            } else {
              return 0.64285714f;
            }
          }
        }
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_137(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_138(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_139(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[1] <= 9.14353895f) {
      if (x[5] <= 1.40265620f) {
        if (x[5] <= 1.40253848f) {
          if (x[4] <= 2.56777543f) {
            if (x[6] <= -13.27052164f) {
              return 0.80952381f;
            } else {
              if (x[0] <= -0.64160737f) {
                if (x[7] <= 5.01412058f) {
                  if (x[6] <= -2.92484844f) {
                    if (x[6] <= -3.98207057f) {
                      return 0.91304348f;
                    } else {
                      return 0.96212121f;
                    }
                  } else {
                    if (x[0] <= -0.66638216f) {
                      return 0.92124930f;
                    } else {
                      return 0.90966667f;
                    }
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[3] <= 0.00074339f) {
                  if (x[7] <= -0.08320007f) {
                    if (x[0] <= 1.45805573f) {
                      return 0.00184502f;
                    } else {
                      return 0.03875316f;
                    }
                  } else {
                    if (x[1] <= -0.32646950f) {
                      return 0.13541667f;
                    } else {
                      return 0.04919584f;
                    }
                  }
                } else {
                  return 1.00000000f;
                }
              }
            }
          } else {
            if (x[6] <= 0.30974765f) {
              if (x[3] <= -4.53409100f) {
                if (x[7] <= -0.13354398f) {
                  return 0.00000000f;
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                return 1.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          return 0.80000000f;
        }
      } else {
        if (x[3] <= -1.51086811f) {
          if (x[6] <= -0.30696522f) {
            if (x[7] <= 1.75435257f) {
              if (x[0] <= -0.67257586f) {
                if (x[5] <= 1.40869331f) {
                  return 0.55555556f;
                } else {
                  return 0.78571429f;
                }
              } else {
                return 0.78947368f;
              }
            } else {
              if (x[4] <= 2.56777543f) {
                return 0.00000000f;
              } else {
                return 0.63636364f;
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          return 1.00000000f;
        }
      }
    } else {
      if (x[7] <= 1.20056957f) {
        return 0.00000000f;
      } else {
        if (x[5] <= -0.16012021f) {
          return 1.00000000f;
        } else {
          return 0.95454545f;
        }
      }
    }
  }
}

static float rf_tree_140(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[4] <= 0.63412052f) {
      if (x[7] <= 4.08225489f) {
        if (x[1] <= 0.30244550f) {
          if (x[0] <= -0.68496326f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[6] <= 0.24832809f) {
              if (x[0] <= -0.68186641f) {
                if (x[1] <= -0.10876816f) {
                  return 0.00000000f;
                } else {
                  if (x[6] <= -0.44541095f) {
                    return 0.00000000f;
                  } else {
                    return 0.86666667f;
                  }
                }
              } else {
                if (x[5] <= -1.25234950f) {
                  if (x[0] <= 1.51379895f) {
                    if (x[1] <= 0.10893319f) {
                      return 0.05186020f;
                    } else {
                      return 0.22500000f;
                    }
                  } else {
                    if (x[6] <= -0.53149903f) {
                      return 0.18385292f;
                    } else {
                      return 0.12160695f;
                    }
                  }
                } else {
                  if (x[1] <= 0.19359483f) {
                    if (x[6] <= 0.21761830f) {
                      return 0.04211843f;
                    } else {
                      return 0.09966777f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              }
            } else {
              if (x[7] <= -0.29162385f) {
                if (x[0] <= -0.67325717f) {
                  if (x[5] <= 1.40572560f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[0] <= -0.67839792f) {
                      return 0.00000000f;
                    } else {
                      return 0.59259259f;
                    }
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        } else {
          if (x[5] <= -1.41387981f) {
            return 0.13513514f;
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[5] <= -1.41204119f) {
          if (x[5] <= -1.41215628f) {
            return 0.88888889f;
          } else {
            return 0.77777778f;
          }
        } else {
          if (x[6] <= -4.09131694f) {
            if (x[7] <= 9.07536364f) {
              if (x[0] <= 1.75844997f) {
                if (x[7] <= 4.35662913f) {
                  if (x[5] <= 1.39409876f) {
                    return 0.00000000f;
                  } else {
                    return 0.54545455f;
                  }
                } else {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[5] <= -1.16940039f) {
              return 0.00000000f;
            } else {
              return 0.73913043f;
            }
          }
        }
      }
    } else {
      if (x[1] <= 9.14353895f) {
        if (x[0] <= -0.64160737f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[4] <= 2.56777543f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[1] <= 5.76916814f) {
              if (x[4] <= 4.50143015f) {
                if (x[5] <= 0.91924953f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[7] <= 5.21549630f) {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    return 0.99137931f;
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              return 0.86666667f;
            }
          }
        }
      } else {
        if (x[3] <= -1.51086811f) {
          return 0.50000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  }
}

static float rf_tree_141(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_142(const float* x) {
  if (x[6] <= 0.24832809f) {
    if (x[5] <= -0.85195106f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[1] <= -0.47015239f) {
        if (x[0] <= -0.57657355f) {
          if (x[5] <= 1.40929431f) {
            if (x[1] <= -0.94038731f) {
              if (x[5] <= -1.40601110f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[4] <= 2.56777543f) {
                  if (x[5] <= 1.12619120f) {
                    if (x[7] <= -0.31327173f) {
                      return 0.00013098f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    if (x[0] <= -0.63231683f) {
                      return 0.00000000f;
                    } else {
                      return 0.03896104f;
                    }
                  }
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[0] <= -0.67839792f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[4] <= 2.56777543f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[5] <= 1.40251565f) {
                    return 1.00000000f;
                  } else {
                    return 0.94444444f;
                  }
                }
              }
            }
          } else {
            if (x[0] <= -0.62612313f) {
              if (x[5] <= 1.40930313f) {
                return 0.72727273f;
              } else {
                if (x[0] <= -0.68353871f) {
                  return 0.00000000f;
                } else {
                  if (x[1] <= -1.30612558f) {
                    return 0.00000000f;
                  } else {
                    if (x[0] <= -0.64934948f) {
                      return 0.50000000f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              }
            } else {
              return 0.78571429f;
            }
          }
        } else {
          if (x[4] <= 2.56777543f) {
            if (x[5] <= -0.75492921f) {
              if (x[0] <= 0.83249235f) {
                if (x[6] <= 0.30974765f) {
                  return 0.00000000f;
                } else {
                  if (x[1] <= -1.19727486f) {
                    if (x[1] <= -1.41497624f) {
                      return 0.00000000f;
                    } else {
                      return 0.46666667f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                }
              } else {
                if (x[1] <= -1.63267761f) {
                  if (x[5] <= -0.78567597f) {
                    return 0.00000000f;
                  } else {
                    return 0.90000000f;
                  }
                } else {
                  if (x[5] <= -0.77641368f) {
                    if (x[5] <= -1.26925796f) {
                      return 0.04861111f;
                    } else {
                      return 0.01510574f;
                    }
                  } else {
                    if (x[5] <= -0.76258999f) {
                      return 0.76923077f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                }
              }
            } else {
              if (x[6] <= 0.31327173f) {
                return 0.00000000f;
              } else {
                if (x[0] <= 1.50760531f) {
                  if (x[1] <= -0.76187220f) {
                    return 0.00000000f;
                  } else {
                    return 0.01114650f;
                  }
                } else {
                  if (x[5] <= 0.69556659f) {
                    return 0.00000000f;
                  } else {
                    if (x[5] <= 0.73448741f) {
                      return 0.63636364f;
                    } else {
                      return 0.01851852f;
                    }
                  }
                }
              }
            }
          } else {
            if (x[6] <= 0.30974765f) {
              if (x[0] <= 0.11402358f) {
                return 1.00000000f;
              } else {
                return 0.94444444f;
              }
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        if (x[4] <= 2.56777543f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_143(const float* x) {
  if (x[4] <= 0.63412052f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[1] <= -3.15658700f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_144(const float* x) {
  if (x[2] <= 1.31395578f) {
    return 0.00000000f;
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_145(const float* x) {
  if (x[1] <= -0.47015239f) {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[0] <= -0.68496326f) {
      if (x[3] <= 1.51235481f) {
        if (x[5] <= 0.19651026f) {
          if (x[3] <= -1.51086811f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[4] <= 1.60094798f) {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[6] <= 0.31327173f) {
            if (x[4] <= 2.56777543f) {
              if (x[5] <= 1.03618050f) {
                if (x[3] <= -1.51086811f) {
                  return 0.00000000f;
                } else {
                  return 0.01364113f;
                }
              } else {
                return 0.00000000f;
              }
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[4] <= 2.56777543f) {
              if (x[5] <= 1.13711697f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 0.63412052f) {
        if (x[6] <= -4.07319689f) {
          if (x[6] <= -4.09534431f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        } else {
          if (x[0] <= 1.05856228f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[5] <= 1.12283450f) {
              if (x[1] <= -0.19342980f) {
                if (x[1] <= -0.30228046f) {
                  if (x[1] <= -0.41113113f) {
                    if (x[5] <= -1.29791212f) {
                      return 0.00000000f;
                    } else {
                      return 0.07482305f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[5] <= -0.79951161f) {
                    if (x[0] <= 1.45495886f) {
                      return 0.15121951f;
                    } else {
                      return 0.32989691f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        }
      } else {
        if (x[3] <= -1.51086811f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          return 1.00000000f;
        }
      }
    }
  }
}

static float rf_tree_146(const float* x) {
  if (x[7] <= 0.80587333f) {
    if (x[3] <= 1.51235481f) {
      if (x[6] <= 0.24832809f) {
        if (x[4] <= 2.56777543f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[6] <= -0.69713050f) {
            if (x[3] <= -1.51086811f) {
              return 0.83333333f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[5] <= -1.41382951f) {
              return 0.93548387f;
            } else {
              if (x[1] <= 0.10893319f) {
                if (x[7] <= 0.49575487f) {
                  if (x[3] <= -4.53409100f) {
                    return 0.28571429f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[1] <= -0.10876816f) {
                    return 0.99487179f;
                  } else {
                    return 1.00000000f;
                  }
                }
              } else {
                if (x[7] <= 0.49575487f) {
                  if (x[1] <= 0.54433589f) {
                    return 1.00000000f;
                  } else {
                    if (x[7] <= -0.03285616f) {
                      return 1.00000000f;
                    } else {
                      return 0.98333333f;
                    }
                  }
                } else {
                  if (x[6] <= -0.52092680f) {
                    return 0.99425287f;
                  } else {
                    return 0.90322581f;
                  }
                }
              }
            }
          }
        }
      } else {
        if (x[0] <= -0.67839792f) {
          if (x[4] <= 2.56777543f) {
            if (x[0] <= -0.71902859f) {
              if (x[0] <= -0.72831911f) {
                if (x[7] <= -0.30974765f) {
                  if (x[1] <= -0.10876816f) {
                    if (x[1] <= -0.32646950f) {
                      return 0.00000000f;
                    } else {
                      return 0.00750751f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[0] <= -0.72522229f) {
                  if (x[3] <= -1.51086811f) {
                    return 0.00000000f;
                  } else {
                    return 0.05343511f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              if (x[0] <= -0.71648917f) {
                return 0.04123711f;
              } else {
                if (x[1] <= 0.32663454f) {
                  if (x[1] <= 0.10893319f) {
                    if (x[6] <= 0.31327173f) {
                      return 0.00000000f;
                    } else {
                      return 0.00835232f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            if (x[0] <= -0.71283489f) {
              return 1.00000000f;
            } else {
              if (x[2] <= 1.31395578f) {
                return 0.00000000f;
              } else {
                return 1.00000000f;
              }
            }
          }
        } else {
          if (x[1] <= 0.47031744f) {
            if (x[6] <= 0.26997598f) {
              return 0.00000000f;
            } else {
              if (x[1] <= -0.47015239f) {
                if (x[3] <= -1.51086811f) {
                  if (x[0] <= -0.63851053f) {
                    if (x[4] <= 4.50143015f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    if (x[5] <= 1.27127230f) {
                      return 0.56497175f;
                    } else {
                      return 0.23529412f;
                    }
                  }
                } else {
                  if (x[1] <= -0.94038731f) {
                    if (x[1] <= -4.08834863f) {
                      return 0.28000000f;
                    } else {
                      return 0.06353055f;
                    }
                  } else {
                    if (x[4] <= 1.60094798f) {
                      return 0.01755786f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                if (x[4] <= 2.56777543f) {
                  if (x[0] <= -0.67567271f) {
                    if (x[4] <= 0.63412052f) {
                      return 0.23321555f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  if (x[4] <= 14.16970444f) {
                    if (x[3] <= -4.53409100f) {
                      return 0.48497854f;
                    } else {
                      return 1.00000000f;
                    }
                  } else {
                    return 0.94117647f;
                  }
                }
              }
            }
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      }
    } else {
      return 1.00000000f;
    }
  } else {
    if (x[4] <= 0.63412052f) {
      if (x[0] <= 0.08924880f) {
        if (x[1] <= -0.47015239f) {
          return 0.00000000f;
        } else {
          if (x[7] <= 2.49189079f) {
            if (x[5] <= 0.80152711f) {
              if (x[0] <= -0.60134834f) {
                if (x[0] <= -0.65399477f) {
                  if (x[1] <= 0.10893319f) {
                    if (x[1] <= -0.32646950f) {
                      return 0.00000000f;
                    } else {
                      return 0.01776199f;
                    }
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                } else {
                  return 0.00000000f;
                }
              } else {
                if (x[5] <= 0.76020250f) {
                  if (x[6] <= -1.30125737f) {
                    if (x[6] <= -1.35160130f) {
                      return 0.03603604f;
                    } else {
                      return 0.60000000f;
                    }
                  } else {
                    if (x[7] <= 0.89850613f) {
                      return 0.07407407f;
                    } else {
                      return 0.00000000f;
                    }
                  }
                } else {
                  return 0.75000000f;
                }
              }
            } else {
              if (x[0] <= -0.62612313f) {
                return 0.00000000f;
              } else {
                if (x[0] <= -0.62302628f) {
                  return 0.50000000f;
                } else {
                  return 0.00000000f;
                }
              }
            }
          } else {
            if (x[7] <= 2.50095272f) {
              if (x[5] <= -0.59853759f) {
                return 0.70000000f;
              } else {
                return 0.00000000f;
              }
            } else {
              if (x[6] <= -2.90169024f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                if (x[7] <= 2.89262831f) {
                  return 0.04360465f;
                } else {
                  if (x[5] <= -0.14906077f) {
                    return 0.00000000f;
                  } else {
                    return 0.62500000f;
                  }
                }
              }
            }
          }
        }
      } else {
        if (x[5] <= -0.85067672f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        }
      }
    } else {
      if (x[3] <= -1.51086811f) {
        if (x[7] <= 0.92367807f) {
          if (x[5] <= 0.21104669f) {
            if (x[1] <= 0.54433590f) {
              if (x[1] <= -0.10876816f) {
                return 0.00000000f;
              } else {
                if (x[5] <= -1.26673144f) {
                  return 0.27272727f;
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              return 0.75000000f;
            }
          } else {
            return 0.00000000f;
          }
        } else {
          if (x[4] <= 4.50143015f) {
            if (x[5] <= -1.08046091f) {
              if (x[5] <= -1.09237713f) {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              } else {
                return 0.72727273f;
              }
            } else {
              if (x[5] <= 0.16070870f) {
                if (x[5] <= 0.12825073f) {
                  if (x[6] <= -2.66054285f) {
                    if (x[6] <= -2.77381670f) {
                      return 0.00000000f;
                    } else {
                      return 0.55555556f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  return 0.40000000f;
                }
              } else {
                return 0.00000000f;
              }
            }
          } else {
            if (x[3] <= -7.55731416f) {
              if (x[6] <= -1.55297691f) {
                return 0.00000000f;
              } else {
                return 0.81818182f;
              }
            } else {
              return 1.00000000f;
            }
          }
        }
      } else {
        return 1.00000000f;
      }
    }
  }
}

static float rf_tree_147(const float* x) {
  if (x[0] <= -0.68496326f) {
    if (x[1] <= -0.32646950f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 0.63412052f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  } else {
    if (x[2] <= 1.31395578f) {
      return 0.00000000f;
    } else {
      return 1.00000000f;
    }
  }
}

static float rf_tree_148(const float* x) {
  if (x[3] <= 1.51235481f) {
    if (x[3] <= -7.55731416f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      if (x[4] <= 2.56777543f) {
        if (x[0] <= -0.68496326f) {
          if (x[2] <= 1.31395578f) {
            return 0.00000000f;
          } else {
            return 1.00000000f;
          }
        } else {
          if (x[1] <= 0.30244550f) {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          } else {
            if (x[0] <= 1.06475598f) {
              if (x[1] <= 0.76203725f) {
                if (x[0] <= -0.66947901f) {
                  if (x[0] <= -0.67325717f) {
                    if (x[4] <= 0.63412052f) {
                      return 0.01443570f;
                    } else {
                      return 0.00000000f;
                    }
                  } else {
                    return 0.00000000f;
                  }
                } else {
                  if (x[5] <= -1.41387981f) {
                    return 0.36363636f;
                  } else {
                    if (x[2] <= 1.31395578f) {
                      return 0.00000000f;
                    } else {
                      return 1.00000000f;
                    }
                  }
                }
              } else {
                if (x[7] <= 4.19603205f) {
                  if (x[2] <= 1.31395578f) {
                    return 0.00000000f;
                  } else {
                    return 1.00000000f;
                  }
                } else {
                  if (x[1] <= 2.50364804f) {
                    return 0.00000000f;
                  } else {
                    if (x[0] <= -0.46353860f) {
                      return 0.46666667f;
                    } else {
                      return 0.14814815f;
                    }
                  }
                }
              }
            } else {
              if (x[6] <= -3.70517898f) {
                if (x[6] <= -5.61824751f) {
                  return 0.00000000f;
                } else {
                  if (x[0] <= 1.51534742f) {
                    if (x[6] <= -4.10944057f) {
                      return 0.00000000f;
                    } else {
                      return 0.66666667f;
                    }
                  } else {
                    if (x[7] <= 4.77498698f) {
                      return 0.00000000f;
                    } else {
                      return 0.60000000f;
                    }
                  }
                }
              } else {
                if (x[2] <= 1.31395578f) {
                  return 0.00000000f;
                } else {
                  return 1.00000000f;
                }
              }
            }
          }
        }
      } else {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      }
    }
  } else {
    return 1.00000000f;
  }
}

static float rf_tree_149(const float* x) {
  if (x[0] <= -0.67839792f) {
    if (x[5] <= -0.87642530f) {
      if (x[0] <= -0.73141596f) {
        if (x[2] <= 1.31395578f) {
          return 0.00000000f;
        } else {
          return 1.00000000f;
        }
      } else {
        if (x[4] <= 0.63412052f) {
          if (x[0] <= -0.68496326f) {
            if (x[0] <= -0.71593174f) {
              if (x[0] <= -0.71902859f) {
                return 0.00000000f;
              } else {
                if (x[5] <= -1.21938908f) {
                  if (x[5] <= -1.33858401f) {
                    return 0.00000000f;
                  } else {
                    return 0.57142857f;
                  }
                } else {
                  return 0.00000000f;
                }
              }
            } else {
              return 0.00000000f;
            }
          } else {
            if (x[6] <= 0.30974765f) {
              return 0.00000000f;
            } else {
              if (x[0] <= -0.68186641f) {
                return 0.66666667f;
              } else {
                return 0.00000000f;
              }
            }
          }
        } else {
          if (x[5] <= -1.31389910f) {
            return 1.00000000f;
          } else {
            if (x[2] <= 1.31395578f) {
              return 0.00000000f;
            } else {
              return 1.00000000f;
            }
          }
        }
      }
    } else {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    }
  } else {
    if (x[3] <= 1.51235481f) {
      if (x[2] <= 1.31395578f) {
        return 0.00000000f;
      } else {
        return 1.00000000f;
      }
    } else {
      return 1.00000000f;
    }
  }
}

// ============================================================
// rf_predict_proba()
// Input:  raw_features[8] -- RAW (unscaled) sensor readings
// Output: P(instability) in [0.0, 1.0]
// Mirrors sklearn CalibratedClassifierCV.predict_proba() exactly:
//   1. StandardScaler normalization
//   2. Average raw leaf probs per fold (50 trees)
//   3. Sigmoid Platt calibration per fold
//   4. Average calibrated probs across 3 folds
// ============================================================
inline float rf_predict_proba(const float* raw_features) {
    float x[8];
    rf_scale_features(raw_features, x);

    // Function pointer table for all 150 trees
    typedef float (*TreeFn)(const float*);
    static const TreeFn ALL_TREES[150] = {
        rf_tree_000,
        rf_tree_001,
        rf_tree_002,
        rf_tree_003,
        rf_tree_004,
        rf_tree_005,
        rf_tree_006,
        rf_tree_007,
        rf_tree_008,
        rf_tree_009,
        rf_tree_010,
        rf_tree_011,
        rf_tree_012,
        rf_tree_013,
        rf_tree_014,
        rf_tree_015,
        rf_tree_016,
        rf_tree_017,
        rf_tree_018,
        rf_tree_019,
        rf_tree_020,
        rf_tree_021,
        rf_tree_022,
        rf_tree_023,
        rf_tree_024,
        rf_tree_025,
        rf_tree_026,
        rf_tree_027,
        rf_tree_028,
        rf_tree_029,
        rf_tree_030,
        rf_tree_031,
        rf_tree_032,
        rf_tree_033,
        rf_tree_034,
        rf_tree_035,
        rf_tree_036,
        rf_tree_037,
        rf_tree_038,
        rf_tree_039,
        rf_tree_040,
        rf_tree_041,
        rf_tree_042,
        rf_tree_043,
        rf_tree_044,
        rf_tree_045,
        rf_tree_046,
        rf_tree_047,
        rf_tree_048,
        rf_tree_049,
        rf_tree_050,
        rf_tree_051,
        rf_tree_052,
        rf_tree_053,
        rf_tree_054,
        rf_tree_055,
        rf_tree_056,
        rf_tree_057,
        rf_tree_058,
        rf_tree_059,
        rf_tree_060,
        rf_tree_061,
        rf_tree_062,
        rf_tree_063,
        rf_tree_064,
        rf_tree_065,
        rf_tree_066,
        rf_tree_067,
        rf_tree_068,
        rf_tree_069,
        rf_tree_070,
        rf_tree_071,
        rf_tree_072,
        rf_tree_073,
        rf_tree_074,
        rf_tree_075,
        rf_tree_076,
        rf_tree_077,
        rf_tree_078,
        rf_tree_079,
        rf_tree_080,
        rf_tree_081,
        rf_tree_082,
        rf_tree_083,
        rf_tree_084,
        rf_tree_085,
        rf_tree_086,
        rf_tree_087,
        rf_tree_088,
        rf_tree_089,
        rf_tree_090,
        rf_tree_091,
        rf_tree_092,
        rf_tree_093,
        rf_tree_094,
        rf_tree_095,
        rf_tree_096,
        rf_tree_097,
        rf_tree_098,
        rf_tree_099,
        rf_tree_100,
        rf_tree_101,
        rf_tree_102,
        rf_tree_103,
        rf_tree_104,
        rf_tree_105,
        rf_tree_106,
        rf_tree_107,
        rf_tree_108,
        rf_tree_109,
        rf_tree_110,
        rf_tree_111,
        rf_tree_112,
        rf_tree_113,
        rf_tree_114,
        rf_tree_115,
        rf_tree_116,
        rf_tree_117,
        rf_tree_118,
        rf_tree_119,
        rf_tree_120,
        rf_tree_121,
        rf_tree_122,
        rf_tree_123,
        rf_tree_124,
        rf_tree_125,
        rf_tree_126,
        rf_tree_127,
        rf_tree_128,
        rf_tree_129,
        rf_tree_130,
        rf_tree_131,
        rf_tree_132,
        rf_tree_133,
        rf_tree_134,
        rf_tree_135,
        rf_tree_136,
        rf_tree_137,
        rf_tree_138,
        rf_tree_139,
        rf_tree_140,
        rf_tree_141,
        rf_tree_142,
        rf_tree_143,
        rf_tree_144,
        rf_tree_145,
        rf_tree_146,
        rf_tree_147,
        rf_tree_148,
        rf_tree_149
    };

    float calibrated_avg = 0.0f;
    for (int fold = 0; fold < 3; fold++) {
        float fold_raw = 0.0f;
        for (int t = 0; t < 50; t++) {
            fold_raw += ALL_TREES[fold * 50 + t](x);
        }
        fold_raw /= 50.0f;
        calibrated_avg += rf_sigmoid(fold_raw, RF_SIGMOID_A[fold], RF_SIGMOID_B[fold]);
    }
    return calibrated_avg / 3.0f;
}

// Returns predicted class: 0=NORMAL, 1=INSTABILITY
inline int rf_predict_class(const float* raw_features) {
    return (rf_predict_proba(raw_features) >= 0.50f) ? 1 : 0;
}
