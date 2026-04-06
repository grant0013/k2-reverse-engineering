# K2 Motor Controller Parameter Map
# Extracted from klippy.log flash_param enumeration
#
# Status meanings:
#   "not configurable" = firmware-locked, cannot change from config
#   "not need override" = configurable from config, has factory default in MCU flash
#   "result is None" = parameter exists but returned no value
#   "write success" = parameter was written successfully

## System Parameters (0-7)
| ID | Key | Status |
|----|-----|--------|
| 0 | param_flash_param_version | not configurable |
| 1 | param_boot_key | not configurable |
| 2 | param_flash_key_write_retries_num | not configurable |
| 3 | param_system_startup_delay_ms | not configurable |
| 4 | param_pwm_period_s | not configurable |
| 5 | param_task_period_s | not configurable |
| 6 | param_use_default_param | not configurable |
| 7 | param_singleturn_control_mode | not configurable |

## Calibration Parameters (8-25)
| ID | Key | Status |
|----|-----|--------|
| 8 | param_elec_angle_calibration_standar_deg | not configurable |
| 9 | param_elec_offset | result is None |
| 10 | param_phase_order_invert | result is None |
| 11 | param_emergency_pin_mode | not configurable |
| 12 | param_stall_mode | CONFIGURABLE |
| 13 | param_stall_cur_A | CONFIGURABLE |
| 14 | param_stall_pos_err_rad | CONFIGURABLE |
| 15 | param_calibration_dir | not configurable |
| 16 | param_encoder_cal_count_max | not configurable |
| 17 | param_encoder_read_count | not configurable |
| 18 | param_delay_ms_per_step | not configurable |
| 19 | param_delay_ms_per_read | not configurable |
| 20 | param_ud_cal_set | CONFIGURABLE |
| 21 | param_motion_dir | CONFIGURABLE |
| 22 | param_encoder_calibtate_official_cal_count_max | not configurable |
| 23 | param_encoder_calibtate_official_ud_cal_set | CONFIGURABLE |
| 24 | param_encoder_calibration_round_count | not configurable |
| 25 | param_elec_offset_err_deg | result is None |

## Driver Board Parameters (26-40)
| ID | Key | Status |
|----|-----|--------|
| 26 | driver_board_param_power_supply_V | not configurable |
| 27 | driver_board_param_adc_ref_V | not configurable |
| 28 | driver_board_param_amp_gain | not configurable |
| 29 | driver_board_param_power_voltage_sample_gain | not configurable |
| 30 | driver_board_param_R_of_current_sample_ohm | not configurable |
| 31 | driver_board_param_adc_calibration_start_index | not configurable |
| 32 | driver_board_param_adc_calibration_buffer_size | not configurable |
| 33 | driver_board_param_led_toggle_period_s | not configurable |
| 34 | driver_board_param_current_dir | not configurable |
| 35 | driver_board_param_pwm_output_en | not configurable |
| 36 | driver_board_param_mos_Ron | not configurable |
| 37 | driver_board_param_mos_deadtime | not configurable |
| 38 | driver_board_param_mos_rise_fall_time | not configurable |
| 39 | driver_board_param_mos_max_peak_current | not configurable |
| 40 | driver_board_param_mos_max_continuous_current | not configurable |

## Motor Electrical Parameters (41-54)
| ID | Key | Status |
|----|-----|--------|
| 41 | motor_param_R | CONFIGURABLE |
| 42 | motor_param_L | CONFIGURABLE |
| 43 | motor_param_Ke | CONFIGURABLE |
| 44 | motor_param_Kt | not configurable |
| 45 | motor_param_mass | not configurable |
| 46 | motor_param_J | not configurable |
| 47 | motor_param_B | not configurable |
| 48 | motor_param_stepping_angle_degree | not configurable |
| 49 | motor_param_phase_nums | not configurable |
| 50 | motor_param_pole_pair | not configurable |
| 51 | motor_param_power_supply | not configurable |
| 52 | motor_param_rated_voltage | not configurable |
| 53 | motor_param_rated_current | not configurable |
| 54 | motor_param_maximum_holding_torque | not configurable |

## Encoder Parameters (55-64)
| ID | Key | Status |
|----|-----|--------|
| 55 | encoder_param_direction | not configurable |
| 56 | encoder_param_encoder_bit | not configurable |
| 57 | encoder_param_encoder_max_pulse | not configurable |
| 58 | encoder_param_fake_encoder_en | not configurable |
| 59 | encoder_param_fake_encoder_step | not configurable |
| 60 | mcu_param_sysclk_hz | not configurable |
| 61 | mcu_param_HSE_hz | not configurable |
| 62 | mcu_param_uart_baudrate | not configurable |
| 63 | mcu_param_input_pulse_counter_trigger_mode | not configurable |
| 64 | mcu_param_input_pulse_counter_filter_level | not configurable |

## Controller Parameters (65-167)
| ID | Key | Status |
|----|-----|--------|
| 65 | controller_param_control_algorithm | not configurable |
| 66 | controller_param_en_feedforward_idiq | CONFIGURABLE |
| 67 | controller_param_en_feedforward_uduq | CONFIGURABLE |
| 68 | controller_pos_loop_pid_param_en | not configurable |
| 69 | controller_pos_loop_pid_param_bypass | not configurable |
| 70 | controller_pos_loop_pid_param_kp | CONFIGURABLE |
| 71 | controller_pos_loop_pid_param_ki | not configurable |
| 72 | controller_pos_loop_pid_param_kd | not configurable |
| 73 | controller_pos_loop_pid_param_kc | not configurable |
| 74 | controller_pos_loop_pid_ud_filter_param_en | not configurable |
| 75 | controller_pos_loop_pid_ud_filter_param_fc | not configurable |
| 76 | controller_pos_loop_pid_param_limit_ui | not configurable |
| 77 | controller_pos_loop_pid_parma_limit_out | not configurable |
| 78 | controller_pos_loop_pid_fal_param_en | not configurable |
| 79 | controller_pos_loop_pid_fal_param_a | not configurable |
| 80 | controller_pos_loop_pid_fal_param_d | not configurable |
| 81 | controller_pos_loop_pid_fal_param_zoom | not configurable |
| 82 | controller_pos_loop_pid_fal_param_section_nums | not configurable |
| 83 | controller_pos_loop_pid_fal_param_inteval_gain | not configurable |
| 84 | controller_spd_loop_pid_param_en | not configurable |
| 85 | controller_spd_loop_pid_param_bypass | not configurable |
| 86 | controller_spd_loop_pid_param_kp | CONFIGURABLE |
| 87 | controller_spd_loop_pid_param_ki | CONFIGURABLE |
| 88 | controller_spd_loop_pid_param_kd | not configurable |
| 89 | controller_spd_loop_pid_param_kc | CONFIGURABLE |
| 90 | controller_spd_loop_pid_ud_filter_param_en | not configurable |
| 91 | controller_spd_loop_pid_ud_filter_param_fc | not configurable |
| 92 | controller_spd_loop_pid_param_limit_ui | not configurable |
| 93 | controller_spd_loop_pid_parma_limit_out | not configurable |
| 94 | controller_spd_loop_pid_fal_param_en | CONFIGURABLE |
| 95 | controller_spd_loop_pid_fal_param_a | CONFIGURABLE |
| 96 | controller_spd_loop_pid_fal_param_d | not configurable |
| 97 | controller_spd_loop_pid_fal_param_zoom | CONFIGURABLE |
| 98 | controller_spd_loop_pid_fal_param_section_nums | not configurable |
| 99 | controller_spd_loop_pid_fal_param_inteval_gain | not configurable |
| 100 | controller_cur_loop_pid_param_en | not configurable |
| 101 | controller_cur_loop_pid_param_bypass | not configurable |
| 102 | controller_cur_loop_pid_param_kp | CONFIGURABLE |
| 103 | controller_cur_loop_pid_param_ki | CONFIGURABLE |
| 104 | controller_cur_loop_pid_param_kd | not configurable |
| 105 | controller_cur_loop_pid_param_kc | CONFIGURABLE |
| 106 | controller_cur_loop_pid_ud_filter_param_en | not configurable |
| 107 | controller_cur_loop_pid_ud_filter_param_fc | not configurable |
| 108 | controller_cur_loop_pid_param_limit_ui | not configurable |
| 109 | controller_cur_loop_pid_parma_limit_out | not configurable |
| 110 | controller_cur_loop_pid_fal_param_en | CONFIGURABLE |
| 111 | controller_cur_loop_pid_fal_param_a | CONFIGURABLE |
| 112 | controller_cur_loop_pid_fal_param_d | not configurable |
| 113 | controller_cur_loop_pid_fal_param_zoom | CONFIGURABLE |
| 114 | controller_cur_loop_pid_fal_param_section_nums | not configurable |
| 115 | controller_cur_loop_pid_fal_param_inteval_gain | not configurable |
| 116 | controller_leso_param_b0k | CONFIGURABLE |
| 117 | controller_leso_param_b0 | not configurable |
| 118 | controller_leso_param_z3k | CONFIGURABLE |
| 119 | controller_leso_param_wp | CONFIGURABLE |
| 120 | controller_leso_param_ws | CONFIGURABLE |
| 121 | controller_leso_param_wd | CONFIGURABLE |
| 122 | controller_fwc_param_en | CONFIGURABLE |
| 123 | controller_fwc_param_I_max | CONFIGURABLE |
| 124 | controller_fwc_param_L | not configurable |
| 125 | controller_fwc_param_phi_e | not configurable |
| 126 | controller_fwc_param_pole_pair | not configurable |
| 127 | controller_fwc_param_wm_base | CONFIGURABLE |
| 128 | controller_cur_filter_param_en | CONFIGURABLE |
| 129 | controller_cur_filter_param_Ts | not configurable |
| 130 | controller_cur_filter_param_fc | CONFIGURABLE |
| 131-135 | controller_z3_filter_binary_second_order_param_* | not configurable |
| 136-140 | controller_spd_out_filter_binary_second_order_param_* | not configurable |
| 141 | controller_td_param_en | CONFIGURABLE |
| 142 | controller_td_param_h0_gain_h | CONFIGURABLE |
| 143 | controller_td_fhan_param_f0 | CONFIGURABLE |
| 144 | controller_td_param_d_gain | CONFIGURABLE |
| 145 | controller_td_param_dd_gain | CONFIGURABLE |
| 146-157 | controller_spd_out_filter_notch_*_param_* | not configurable |
| 158-167 | controller_motor_ripple_compensator_* | not configurable |

## Flash/System Parameters (168-172)
| ID | Key | Status |
|----|-----|--------|
| 168 | flash_manager_param_checksum_restore_en | not configurable |
| 169-172 | logger_param_* | not configurable |

## Protection Parameters (173-192)
| ID | Key | Status |
|----|-----|--------|
| 173 | protection_param_protect_en | CONFIGURABLE |
| 174 | protection_param_protect_report | not configurable |
| 175 | protection_param_err_code_mask | not configurable |
| 176 | protection_param_warning_code_mask | not configurable |
| 177-178 | protection_param_encoder_mutation_coefficient_* | not configurable |
| 179 | protection_param_prt_peak_cur_A | CONFIGURABLE |
| 180 | protection_param_prt_continuous_cur_A | CONFIGURABLE |
| 181 | protection_param_prt_continuous_time_s | CONFIGURABLE |
| 182 | protection_param_prt_over_speed_rad_s | CONFIGURABLE |
| 183 | protection_param_prt_over_speed_time_s | CONFIGURABLE |
| 184-186 | protection_param_pos_over_limit_* / cmd_mutation_* | not configurable |
| 187 | protection_param_prt_track_max_err | CONFIGURABLE |
| 188 | protection_param_prt_track_err_time | CONFIGURABLE |
| 189 | protection_param_power_voltage_min | CONFIGURABLE |
| 190 | protection_param_mcu_temp_max | CONFIGURABLE |
| 191-192 | protection_err/warning_code_backup | not configurable |

## Chopper Parameters (193-198)
| ID | Key | Status |
|----|-----|--------|
| 193-198 | chopper_param_* | not configurable |

## Step Controller Parameters (199-204)
| ID | Key | Status |
|----|-----|--------|
| 199 | step_controller_param_pulse_count_max | not configurable |
| 200 | step_controller_param_subdivision | CONFIGURABLE |
| 201-203 | step_controller_param_pulse_trim_* | not configurable |
| 204 | cmd_int_param_char_cmd_support | CONFIGURABLE |

## System ID Parameters (205-216)
| ID | Key | Status |
|----|-----|--------|
| 205-214 | system_id_RL_param_* | not configurable |
| 215-216 | motor_phase_check_param_* | not configurable |

## Zazen (Idle) Parameters (217-223)
| ID | Key | Status |
|----|-----|--------|
| 217 | zazen_param_zazen_en | CONFIGURABLE |
| 218 | zazen_param_zazen_trigger_time_s | CONFIGURABLE |
| 219 | zazen_param_zazen_gain_pos_kp | not configurable |
| 220 | zazen_param_zazen_gain_spd_kp | CONFIGURABLE |
| 221 | zazen_param_zazen_gain_spd_ki | CONFIGURABLE |
| 222 | zazen_param_zazen_gain_cur_kp | CONFIGURABLE |
| 223 | zazen_param_zazen_gain_cur_ki | CONFIGURABLE |

## Flash Key Parameters (224-226)
| ID | Key | Status |
|----|-----|--------|
| 224 | param_flash_key | not configurable |
| 225 | param_flash_checksum | not configurable |
| 226 | stall_pos_err_rad_for_slicer | CONFIGURABLE |
