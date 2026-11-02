# Implementation coverage

| Assessment technique / feature | Implementation status | Evidence / caveat |
|---|---|---|
| Predictive trim | Implemented | MCU BG/HSI/LDO and PMIC 7 trim-code regressors |
| Transfer learning | Implemented for MCU-C BG drift | MCU-A base, 50 MCU-C fine-tuning samples, held-out MCU-C evaluation |
| Wafer-map spatial prediction | Partial | Wafer XY/radius are model features; no dedicated sparse wafer-map GP/CNN because no sparse sampling protocol is supplied |
| Coupled multi-trim optimization | Partial | PMIC outputs predicted separately; no validated coupled response surface supplied |
| Drift-aware calibration targets | Partial | MCU sort-to-final BG shift model and sensor post-reflow shift estimates |
| Fuse-map generation and validation | Validation implemented | Schema decode and per-die trim-field join; no general fuse-map spec generator |
| Die-to-SKU assignment | Per-die feasibility implemented | Uses core count and Fmax; no global demand-constrained optimizer or TDP proof |
| Memory repair allocation | Implemented | Exact binary row/column redundancy solver |
| Anomaly screening | Implemented | Unsupervised IsolationForest, feature-only |
| MCU workflows | Implemented where labels/features support | BG, HSI, LDO, TS hot-point, SRAM record context, fuse validation; no standalone ADC/LSI model in source data |
| PMIC workflows | Implemented where supported | Reference/rails/OVP/UVLO/ILIM trim, current-sense features, OTP rule validation |
| Sensor workflows | Implemented where supported | X/Y/Z TCO/TCS and post-reflow shift prediction; no quadratic TCO target model |
| SoC workflows | Implemented where supported | Slowest healthy Fmax, worst healthy Vmin, core count/harvesting context, L2 repair data, SKU feasibility |

No physical trim, fuse or OTP operation is performed. The original assessment's safety and verification requirements take precedence over model predictions.
