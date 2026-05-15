/*
Copyright 2021 @Yowkees
Copyright 2022 MURAOKA Taro (aka KoRoN, @kaoriya)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#pragma once

// Key matrix parameters (Keyball61 is duplex matrix)
#define MATRIX_ROWS         (5 * 2)  // split keyboard
#define MATRIX_COLS         (4 * 2)  // duplex matrix
#define MATRIX_ROW_PINS     { GP4, GP5, GP6, GP7, GP8 }
#define MATRIX_COL_PINS     { GP29, GP28, GP27, GP26 }
#define MATRIX_MASKED
#define DEBOUNCE            5

// Split parameters
#define SERIAL_USART_TX_PIN GP1
#define SPLIT_HAND_MATRIX_GRID  GP26, GP6
#define SPLIT_HAND_MATRIX_GRID_LOW_IS_LEFT
// #define SPLIT_USB_DETECT
// #define SPLIT_USB_TIMEOUT       500


#define SPLIT_TRANSACTION_IDS_KB KEYBALL_GET_INFO

// Encoder press/release gap. Windows needs >0 ms between the v=1 and v=0
// wheel reports or it drops the event. 10 ms matches what QMK's own
// non-encoder-map default path uses (tap_code_delay(..., 10)).
#define ENCODER_MAP_KEY_DELAY 10

// Parent keyball/config.h advertises POINTING_DEVICE_HIRES_SCROLL_ENABLE,
// which tells the OS to divide wheel deltas by 120. mousekey's default
// wheel_unit() is 1, which becomes 1/120 of a scroll line — invisible.
// Bump the base wheel delta so MS_WHLU/MS_WHLD send one full hires notch.
#define MOUSEKEY_WHEEL_DELTA 120

// RGB Matrix settings
// Left:  32 per-key + 6 underglow = 38
// Right: 29 per-key + 6 underglow = 35
#ifdef RGB_MATRIX_ENABLE
#    define RGB_MATRIX_MAXIMUM_BRIGHTNESS 120  // limit for power consumption
#    define RGB_MATRIX_SLEEP                   // turn off LEDs when host is asleep
#endif
