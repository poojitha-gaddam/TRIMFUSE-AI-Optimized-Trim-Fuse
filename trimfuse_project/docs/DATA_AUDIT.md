# Dataset audit

Source: original assessment ZIP. CSVs in `datasets/original/` are unchanged copies.

## File-level summary

| File | Primary key | Rows | Columns | Missing cells | Duplicate rows | Duplicate keys |
|---|---|---:|---:|---:|---:|---:|
| `mcu_fuse_map_audit.csv` | `die_id` | 1,500 | 5 | 0 | 0 | 0 |
| `mcu_fuse_schema.csv` | `field` | 10 | 7 | 0 | 0 | 0 |
| `mcu_trim_fuse.csv` | `die_id` | 8,420 | 42 | 0 | 0 | 0 |
| `memory_repair_bitmaps.csv` | `array_id` | 3,000 | 13 | 3,526 | 0 | 0 |
| `pmic_otp_config_requests.csv` | `request_id` | 400 | 10 | 0 | 0 | 0 |
| `pmic_trim_otp.csv` | `die_id` | 11,060 | 63 | 0 | 0 | 0 |
| `sensor_calibration.csv` | `die_id` | 11,060 | 67 | 0 | 0 | 0 |
| `soc_binning_harvesting.csv` | `die_id` | 6,160 | 52 | 10,668 | 0 | 0 |
| `soc_sku_demand.csv` | `sku` | 3 | 6 | 0 | 0 | 0 |

## Column-level dictionary

### `mcu_fuse_map_audit.csv`

| Column | Pandas dtype | Assessment role | Missing |
|---|---|---|---:|
| `die_id` | `object` | id | 0 |
| `derivative` | `object` | meta | 0 |
| `fuse_map_hex` | `object` | label | 0 |
| `has_error` | `bool` | label | 0 |
| `error_type` | `object` | label | 0 |

### `mcu_fuse_schema.csv`

| Column | Pandas dtype | Assessment role | Missing |
|---|---|---|---:|
| `field` | `object` | meta | 0 |
| `lsb` | `int64` | meta | 0 |
| `nbits` | `int64` | meta | 0 |
| `description` | `object` | meta | 0 |
| `MCU-A` | `object` | meta | 0 |
| `MCU-B` | `object` | meta | 0 |
| `MCU-C` | `object` | meta | 0 |

### `mcu_trim_fuse.csv`

| Column | Pandas dtype | Assessment role | Missing |
|---|---|---|---:|
| `die_id` | `object` | id | 0 |
| `lot_id` | `object` | meta | 0 |
| `wafer_id` | `object` | meta | 0 |
| `derivative` | `object` | meta | 0 |
| `die_x` | `int64` | feature | 0 |
| `die_y` | `int64` | feature | 0 |
| `x_mm` | `float64` | feature | 0 |
| `y_mm` | `float64` | feature | 0 |
| `radius_mm` | `float64` | feature | 0 |
| `pcm_vth_n_mV` | `float64` | feature | 0 |
| `pcm_vth_p_mV` | `float64` | feature | 0 |
| `pcm_rs_ohm_sq` | `float64` | feature | 0 |
| `pcm_tox_A` | `float64` | feature | 0 |
| `pcm_mobility_rel` | `float64` | feature | 0 |
| `package` | `object` | meta | 0 |
| `temp_grade` | `object` | meta | 0 |
| `latent_defect` | `bool` | label | 0 |
| `bg_untrim_V` | `float64` | feature | 0 |
| `bg_trim_code_opt` | `int64` | label | 0 |
| `bg_trimmed_sort_V` | `float64` | label | 0 |
| `bg_conv_iterations` | `int64` | meta | 0 |
| `hsi_untrim_MHz` | `float64` | feature | 0 |
| `hsi_trim_code_opt` | `int64` | label | 0 |
| `hsi_trimmed_sort_MHz` | `float64` | label | 0 |
| `hsi_conv_iterations` | `int64` | meta | 0 |
| `ldo_untrim_V` | `float64` | feature | 0 |
| `ldo_trim_code_opt` | `int64` | label | 0 |
| `ldo_trimmed_sort_V` | `float64` | label | 0 |
| `ldo_conv_iterations` | `int64` | meta | 0 |
| `ts_cal1_30C_counts` | `int64` | feature | 0 |
| `ts_slope_counts_per_C_true` | `float64` | label | 0 |
| `ts_cal2_110C_counts` | `int64` | label | 0 |
| `ts_cal2_measured_on_tester` | `bool` | meta | 0 |
| `sram_fail_bits` | `int64` | feature | 0 |
| `sram_repairable` | `bool` | label | 0 |
| `conv_trim_time_ms` | `float64` | meta | 0 |
| `sort_pass` | `bool` | label | 0 |
| `bg_final_V` | `float64` | label | 0 |
| `hsi_final_MHz` | `float64` | label | 0 |
| `ldo_final_V` | `float64` | label | 0 |
| `final_pass` | `bool` | label | 0 |
| `fuse_map_hex` | `object` | label | 0 |

### `memory_repair_bitmaps.csv`

| Column | Pandas dtype | Assessment role | Missing |
|---|---|---|---:|
| `array_id` | `object` | id | 0 |
| `die_id` | `object` | id | 0 |
| `array` | `object` | meta | 0 |
| `rows` | `int64` | meta | 0 |
| `cols` | `int64` | meta | 0 |
| `spare_rows` | `int64` | meta | 0 |
| `spare_cols` | `int64` | meta | 0 |
| `n_fail_cells` | `int64` | feature | 0 |
| `fail_cells` | `object` | feature | 167 |
| `greedy_repairable` | `bool` | label | 0 |
| `optimal_repairable` | `bool` | label | 0 |
| `optimal_spare_rows_used` | `object` | label | 1354 |
| `optimal_spare_cols_used` | `object` | label | 2005 |

### `pmic_otp_config_requests.csv`

| Column | Pandas dtype | Assessment role | Missing |
|---|---|---|---:|
| `request_id` | `object` | id | 0 |
| `customer` | `object` | id | 0 |
| `buck1_V` | `float64` | feature | 0 |
| `buck2_V` | `float64` | feature | 0 |
| `ldo1_V` | `float64` | feature | 0 |
| `ldo2_V` | `float64` | feature | 0 |
| `sequence` | `object` | meta | 0 |
| `i2c_addr` | `object` | meta | 0 |
| `other_addresses_on_bus` | `object` | feature | 0 |
| `label` | `object` | label | 0 |

### `pmic_trim_otp.csv`

| Column | Pandas dtype | Assessment role | Missing |
|---|---|---|---:|
| `die_id` | `object` | id | 0 |
| `lot_id` | `object` | meta | 0 |
| `wafer_id` | `object` | meta | 0 |
| `derivative` | `object` | meta | 0 |
| `die_x` | `int64` | feature | 0 |
| `die_y` | `int64` | feature | 0 |
| `x_mm` | `float64` | feature | 0 |
| `y_mm` | `float64` | feature | 0 |
| `radius_mm` | `float64` | feature | 0 |
| `pcm_vth_n_mV` | `float64` | feature | 0 |
| `pcm_vth_p_mV` | `float64` | feature | 0 |
| `pcm_rs_ohm_sq` | `float64` | feature | 0 |
| `pcm_tox_A` | `float64` | feature | 0 |
| `pcm_mobility_rel` | `float64` | feature | 0 |
| `package` | `object` | meta | 0 |
| `latent_defect` | `bool` | label | 0 |
| `vref_untrim_V` | `float64` | feature | 0 |
| `vref_trim_code_opt` | `int64` | label | 0 |
| `vref_trimmed_sort_V` | `float64` | feature | 0 |
| `vref_final_V` | `float64` | label | 0 |
| `buck1_target_V` | `float64` | meta | 0 |
| `buck1_untrim_V` | `float64` | feature | 0 |
| `buck1_trim_code_opt` | `int64` | label | 0 |
| `buck1_trimmed_sort_V` | `float64` | label | 0 |
| `buck1_final_V` | `float64` | label | 0 |
| `buck2_target_V` | `float64` | meta | 0 |
| `buck2_untrim_V` | `float64` | feature | 0 |
| `buck2_trim_code_opt` | `int64` | label | 0 |
| `buck2_trimmed_sort_V` | `float64` | label | 0 |
| `buck2_final_V` | `float64` | label | 0 |
| `ldo1_target_V` | `float64` | meta | 0 |
| `ldo1_untrim_V` | `float64` | feature | 0 |
| `ldo1_trim_code_opt` | `int64` | label | 0 |
| `ldo1_trimmed_sort_V` | `float64` | label | 0 |
| `ldo1_final_V` | `float64` | label | 0 |
| `ldo2_target_V` | `float64` | meta | 0 |
| `ldo2_untrim_V` | `float64` | feature | 0 |
| `ldo2_trim_code_opt` | `int64` | label | 0 |
| `ldo2_trimmed_sort_V` | `float64` | label | 0 |
| `ldo2_final_V` | `float64` | label | 0 |
| `ovp_untrim_V` | `float64` | feature | 0 |
| `ovp_trim_code_opt` | `int64` | label | 0 |
| `ovp_trimmed_V` | `float64` | label | 0 |
| `uvlo_untrim_V` | `float64` | feature | 0 |
| `uvlo_trim_code_opt` | `int64` | label | 0 |
| `uvlo_trimmed_V` | `float64` | label | 0 |
| `ilim_untrim_A` | `float64` | feature | 0 |
| `ilim_trim_code_opt` | `int64` | label | 0 |
| `ilim_trimmed_A` | `float64` | label | 0 |
| `cs_meas_0p5A_A` | `float64` | feature | 0 |
| `cs_meas_2p0A_A` | `float64` | feature | 0 |
| `cs_gain_err_true_pct` | `float64` | label | 0 |
| `cs_offset_true_mA` | `float64` | label | 0 |
| `cs_inl_true_pct` | `float64` | label | 0 |
| `efficiency_1A_pct` | `float64` | feature | 0 |
| `load_reg_mV` | `float64` | feature | 0 |
| `conv_trim_iterations` | `int64` | meta | 0 |
| `conv_trim_time_ms` | `float64` | meta | 0 |
| `sort_pass` | `bool` | label | 0 |
| `final_pass` | `bool` | label | 0 |
| `sequence` | `object` | meta | 0 |
| `i2c_addr` | `object` | meta | 0 |
| `otp_image_hex` | `object` | label | 0 |

### `sensor_calibration.csv`

| Column | Pandas dtype | Assessment role | Missing |
|---|---|---|---:|
| `die_id` | `object` | id | 0 |
| `lot_id` | `object` | meta | 0 |
| `wafer_id` | `object` | meta | 0 |
| `derivative` | `object` | meta | 0 |
| `die_x` | `int64` | feature | 0 |
| `die_y` | `int64` | feature | 0 |
| `x_mm` | `float64` | feature | 0 |
| `y_mm` | `float64` | feature | 0 |
| `radius_mm` | `float64` | feature | 0 |
| `pcm_vth_n_mV` | `float64` | feature | 0 |
| `pcm_vth_p_mV` | `float64` | feature | 0 |
| `pcm_rs_ohm_sq` | `float64` | feature | 0 |
| `pcm_tox_A` | `float64` | feature | 0 |
| `pcm_mobility_rel` | `float64` | feature | 0 |
| `full_scale_g` | `int64` | meta | 0 |
| `nominal_sens_LSB_per_g` | `int64` | meta | 0 |
| `package` | `object` | meta | 0 |
| `latent_defect` | `bool` | label | 0 |
| `stress_gauge_mV` | `float64` | feature | 0 |
| `asic_vref_mV` | `float64` | feature | 0 |
| `mems_resonance_kHz` | `float64` | feature | 0 |
| `mems_q_factor` | `float64` | feature | 0 |
| `characterized_3temp` | `bool` | meta | 0 |
| `st_response_x_mg` | `float64` | feature | 0 |
| `offset_x_m40C_mg` | `float64` | label | 0 |
| `sens_x_m40C_rel` | `float64` | label | 0 |
| `offset_x_25C_mg` | `float64` | feature | 0 |
| `sens_x_25C_rel` | `float64` | feature | 0 |
| `offset_x_85C_mg` | `float64` | label | 0 |
| `sens_x_85C_rel` | `float64` | label | 0 |
| `tco_x_true_mg_per_C` | `float64` | label | 0 |
| `tco2_x_true_mg_per_C2` | `float64` | label | 0 |
| `tcs_x_true_ppm_per_C` | `float64` | label | 0 |
| `post_reflow_offset_shift_x_mg` | `float64` | label | 0 |
| `cal_offset_code_x` | `int64` | label | 0 |
| `cal_tco_code_x` | `int64` | label | 0 |
| `cal_tcs_code_x` | `int64` | label | 0 |
| `st_response_y_mg` | `float64` | feature | 0 |
| `offset_y_m40C_mg` | `float64` | label | 0 |
| `sens_y_m40C_rel` | `float64` | label | 0 |
| `offset_y_25C_mg` | `float64` | feature | 0 |
| `sens_y_25C_rel` | `float64` | feature | 0 |
| `offset_y_85C_mg` | `float64` | label | 0 |
| `sens_y_85C_rel` | `float64` | label | 0 |
| `tco_y_true_mg_per_C` | `float64` | label | 0 |
| `tco2_y_true_mg_per_C2` | `float64` | label | 0 |
| `tcs_y_true_ppm_per_C` | `float64` | label | 0 |
| `post_reflow_offset_shift_y_mg` | `float64` | label | 0 |
| `cal_offset_code_y` | `int64` | label | 0 |
| `cal_tco_code_y` | `int64` | label | 0 |
| `cal_tcs_code_y` | `int64` | label | 0 |
| `st_response_z_mg` | `float64` | feature | 0 |
| `offset_z_m40C_mg` | `float64` | label | 0 |
| `sens_z_m40C_rel` | `float64` | label | 0 |
| `offset_z_25C_mg` | `float64` | feature | 0 |
| `sens_z_25C_rel` | `float64` | feature | 0 |
| `offset_z_85C_mg` | `float64` | label | 0 |
| `sens_z_85C_rel` | `float64` | label | 0 |
| `tco_z_true_mg_per_C` | `float64` | label | 0 |
| `tco2_z_true_mg_per_C2` | `float64` | label | 0 |
| `tcs_z_true_ppm_per_C` | `float64` | label | 0 |
| `post_reflow_offset_shift_z_mg` | `float64` | label | 0 |
| `cal_offset_code_z` | `int64` | label | 0 |
| `cal_tco_code_z` | `int64` | label | 0 |
| `cal_tcs_code_z` | `int64` | label | 0 |
| `conv_test_insertions` | `int64` | meta | 0 |
| `conv_test_time_s` | `float64` | meta | 0 |

### `soc_binning_harvesting.csv`

| Column | Pandas dtype | Assessment role | Missing |
|---|---|---|---:|
| `die_id` | `object` | id | 0 |
| `lot_id` | `object` | meta | 0 |
| `wafer_id` | `object` | meta | 0 |
| `derivative` | `object` | meta | 0 |
| `die_x` | `int64` | feature | 0 |
| `die_y` | `int64` | feature | 0 |
| `x_mm` | `float64` | feature | 0 |
| `y_mm` | `float64` | feature | 0 |
| `radius_mm` | `float64` | feature | 0 |
| `pcm_vth_n_mV` | `float64` | feature | 0 |
| `pcm_vth_p_mV` | `float64` | feature | 0 |
| `pcm_rs_ohm_sq` | `float64` | feature | 0 |
| `pcm_tox_A` | `float64` | feature | 0 |
| `pcm_mobility_rel` | `float64` | feature | 0 |
| `ro_freq_MHz` | `float64` | feature | 0 |
| `cpm_path_delay_ps` | `float64` | feature | 0 |
| `iddq_25C_mA` | `float64` | feature | 0 |
| `core0_defect` | `bool` | label | 0 |
| `core0_fmax_GHz` | `float64` | label | 650 |
| `core0_vmin_2GHz_mV` | `float64` | label | 650 |
| `core1_defect` | `bool` | label | 0 |
| `core1_fmax_GHz` | `float64` | label | 648 |
| `core1_vmin_2GHz_mV` | `float64` | label | 648 |
| `core2_defect` | `bool` | label | 0 |
| `core2_fmax_GHz` | `float64` | label | 657 |
| `core2_vmin_2GHz_mV` | `float64` | label | 657 |
| `core3_defect` | `bool` | label | 0 |
| `core3_fmax_GHz` | `float64` | label | 675 |
| `core3_vmin_2GHz_mV` | `float64` | label | 675 |
| `core4_defect` | `bool` | label | 0 |
| `core4_fmax_GHz` | `float64` | label | 710 |
| `core4_vmin_2GHz_mV` | `float64` | label | 710 |
| `core5_defect` | `bool` | label | 0 |
| `core5_fmax_GHz` | `float64` | label | 648 |
| `core5_vmin_2GHz_mV` | `float64` | label | 648 |
| `core6_defect` | `bool` | label | 0 |
| `core6_fmax_GHz` | `float64` | label | 653 |
| `core6_vmin_2GHz_mV` | `float64` | label | 653 |
| `core7_defect` | `bool` | label | 0 |
| `core7_fmax_GHz` | `float64` | label | 677 |
| `core7_vmin_2GHz_mV` | `float64` | label | 677 |
| `l2_slice0_fail_bits` | `int64` | feature | 0 |
| `l2_slice1_fail_bits` | `int64` | feature | 0 |
| `l2_slice2_fail_bits` | `int64` | feature | 0 |
| `l2_slice3_fail_bits` | `int64` | feature | 0 |
| `l2_repairable` | `bool` | label | 0 |
| `conv_speed_test_time_ms` | `float64` | meta | 0 |
| `sku_rule_based` | `object` | label | 0 |
| `avs_voltage_bin` | `int64` | label | 0 |
| `avs_voltage_V` | `float64` | label | 16 |
| `cores_disabled_mask` | `object` | label | 0 |
| `power_at_sku_W` | `float64` | label | 16 |

### `soc_sku_demand.csv`

| Column | Pandas dtype | Assessment role | Missing |
|---|---|---|---:|
| `sku` | `object` | meta | 0 |
| `cores` | `int64` | meta | 0 |
| `fmax_GHz` | `float64` | meta | 0 |
| `tdp_W` | `float64` | meta | 0 |
| `price_usd` | `int64` | meta | 0 |
| `weekly_demand_units` | `int64` | meta | 0 |

## Important data-quality observations

- `memory_repair_bitmaps.csv` has missing `fail_cells` in 167 rows and missing exact spare-line allocations in many rows. The exact solver only operates when a fail-cell bitmap is present; existing `optimal_repairable` labels are retained for all records.
- `soc_binning_harvesting.csv` has missing per-core Fmax/Vmin values where a core is defective, plus 16 missing values in `avs_voltage_V` and `power_at_sku_W`. These missing values are not imputed into target labels.
- All main datasets have unique `die_id` values and no duplicate full rows in this audit. The memory-repair dataset intentionally has multiple arrays per die; `array_id` is its primary key.
- The three wafer-grouped datasets use `wafer_id`; model validation uses wafer-grouped holdouts to reduce within-wafer leakage.
- Sensor coefficient models are trained only on `characterized_3temp=True` rows, as instructed by the supplied data dictionary.
- Original CSVs are copied without modification. Preprocessing occurs inside saved sklearn pipelines.