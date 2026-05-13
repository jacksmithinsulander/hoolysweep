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

#include QMK_KEYBOARD_H

#include "quantum.h"

// clang-format off
const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
  [0] = LAYOUT_universal(
    KC_ESC   , KC_1     , KC_2     , KC_3     , KC_4     , KC_5     ,                            KC_6     , KC_7     , KC_8     , KC_9     , KC_0     , KC_MINS  ,
    KC_GRV   , KC_Q     , KC_W     , KC_E     , KC_R     , KC_T     ,                            KC_Y     , KC_U     , KC_I     , KC_O     , KC_P     , KC_EQL   ,
    KC_LCTL  , KC_A     , KC_S     , KC_D     , KC_F     , KC_G     ,                            KC_H     , KC_J     , KC_K     , KC_L     , KC_SCLN  , KC_QUOT  ,
    KC_LSFT  , KC_Z     , KC_X     , KC_C     , KC_V     , KC_B     , KC_LBRC  ,      KC_RBRC  , KC_N     , KC_M     , KC_COMM  , KC_DOT   , KC_SLSH  , KC_RSFT  ,
    KC_LGUI  , KC_APP   , KC_HOME  , KC_END   , KC_LALT  , KC_SPC   , KC_TAB   ,      KC_BSPC  , KC_ENT   , KC_RALT  , KC_PGUP  , KC_PGDN  , KC_BSLS  , KC_RGUI
  ),
};

#ifdef ENCODER_MAP_ENABLE
const uint16_t PROGMEM encoder_map[][NUM_ENCODERS][NUM_DIRECTIONS] = {
    [0] = { ENCODER_CCW_CW(MS_WHLD, MS_WHLU), ENCODER_CCW_CW(MS_WHLD, MS_WHLU) },
};
#endif
// clang-format on

void keyboard_post_init_user(void) {
#ifdef RGB_MATRIX_ENABLE
    // Wiring test: indicators_user below lights one LED at a time; use a
    // static-color animation so the base layer doesn't interfere.
    rgb_matrix_enable_noeeprom();
    rgb_matrix_mode_noeeprom(RGB_MATRIX_SOLID_COLOR);
    rgb_matrix_sethsv_noeeprom(0, 0, 0);
#endif
}

#ifdef RGB_MATRIX_ENABLE
// Walk through every LED in chain order, one at a time, coloring each by its
// position in the chain so the highlight sweeps a full rainbow across all
// indices. Watch the spot travel to verify that LED index N is physically
// where keyboard.json's rgb_matrix.layout[N] says it is.
#    define WIRING_TEST_STEP_MS 400
bool rgb_matrix_indicators_user(void) {
    static uint16_t last = 0;
    static uint8_t  idx  = 0;
    if (timer_elapsed(last) >= WIRING_TEST_STEP_MS) {
        last = timer_read();
        idx  = (idx + 1) % RGB_MATRIX_LED_COUNT;
    }
    HSV     hsv = {.h = (uint8_t)((uint16_t)idx * 255 / RGB_MATRIX_LED_COUNT), .s = 255, .v = 255};
    RGB     rgb = hsv_to_rgb(hsv);
    rgb_matrix_set_color_all(0, 0, 0);
    rgb_matrix_set_color(idx, rgb.r, rgb.g, rgb.b);
    return false;
}
#endif

#ifdef OLED_ENABLE

#    include "lib/oledkit/oledkit.h"

void oledkit_render_info_user(void) {
    keyball_oled_render_keyinfo();
    keyball_oled_render_ballinfo();
    keyball_oled_render_layerinfo();
}
#endif
