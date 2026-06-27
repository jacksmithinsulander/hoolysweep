#pragma once

#include QMK_KEYBOARD_H

enum hk_keycodes {
    // Saves the HK configuration to EEPROM. By default any changes to the HK configuration are not saved to EEPROM, so
    // use this if you want your changes to persist.
    HK_SAVE_SETTINGS = QK_KB_0, // 0x7E00

    // Resets the HK configuration to default values. This is unlike QK_CLEAR_EEPROM, which clears all EEPROM data.
    HK_RESET_SETTINGS, // 0x7E01

    // Dumps the HK configuration to the console. Only useful when CONSOLE_ENABLE is set.
    HK_DUMP_SETTINGS, // 0x7E02

    // The behavior the keycodes below enable can be used with either a single or dual pointing device setup. Normally,
    // it's applied to the main side. To apply it to the peripheral side, hold shift.

    // Sets the pointer sensitivity in the corresponding mode. How it's realized depends on the pointing device: a
    // software movement factor for most, or the hardware CPI for sensors that support it. The default is determined by
    // the type of pointing device.
    //
    // Hold these keys and then press + or - to increase or decrease the corresponding sensitivity.
    HK_POINTER_SET_DEFAULT_SENSITIVITY, // 0x7E03
    HK_POINTER_SET_SNIPING_SENSITIVITY, // 0x7E04

    // Sets the scroll buffer size. The buffer acccumulates x/y movements and outputs a h/v value when the thershold is reached.
    //
    // Hold this key and then press + or - to increase or decrease the buffer size.
    HK_POINTER_SET_SCROLL_BUFFER, // 0x7E05

    // Enters sniping mode.
    HK_SNIPING_MODE, // 0x7E06

    // Toggles sniping mode.
    HK_SNIPING_MODE_TOGGLE, // 0x7E07

    // Enters drag-scroll mode. Drag scroll translates x/y movements to h/v movements.
    HK_DRAGSCROLL_MODE, // 0x7E08

    // Toggles drag-scroll mode.
    HK_DRAGSCROLL_MODE_TOGGLE, // 0x7E09

    // Scroll lock filters out any scroll movement that is not in the specified direction. This cycles through the
    // possible modes: off, horizontal, vertical.
    HK_CYCLE_SCROLL_LOCK, // 0x7E0A

    // Inverts the scroll direction.
    HK_INVERT_SCROLL_DIRECTION, // 0x7E0B

    // Toggles the auto-mouse layer at runtime. The layer is enabled at build time
    // via POINTING_DEVICE_AUTO_MOUSE_ENABLE; pointer motion temporarily activates
    // it. Saved with HK_SAVE.
    HK_AUTO_MOUSE_TOGGLE, // 0x7E0C

    // Adjusts the auto-mouse layer timeout (how long it stays active after motion
    // stops) by +/- 50ms. Saved with HK_SAVE.
    HK_AUTO_MOUSE_TIMEOUT_UP,   // 0x7E0D
    HK_AUTO_MOUSE_TIMEOUT_DOWN, // 0x7E0E
};

#define HK_SAVE      HK_SAVE_SETTINGS
#define HK_RESET     HK_RESET_SETTINGS
#define HK_DUMP      HK_DUMP_SETTINGS
#define HK_P_SET_D   HK_POINTER_SET_DEFAULT_SENSITIVITY
#define HK_P_SET_S   HK_POINTER_SET_SNIPING_SENSITIVITY
#define HK_P_SET_BUF HK_POINTER_SET_SCROLL_BUFFER
#define HK_S_MODE    HK_SNIPING_MODE
#define HK_S_MODE_T  HK_SNIPING_MODE_TOGGLE
#define HK_D_MODE    HK_DRAGSCROLL_MODE
#define HK_D_MODE_T  HK_DRAGSCROLL_MODE_TOGGLE
#define HK_C_SCROLL  HK_CYCLE_SCROLL_LOCK
#define HK_I_SCROLL  HK_INVERT_SCROLL_DIRECTION
#define HK_AML_T     HK_AUTO_MOUSE_TOGGLE
#define HK_AML_UP    HK_AUTO_MOUSE_TIMEOUT_UP
#define HK_AML_DN    HK_AUTO_MOUSE_TIMEOUT_DOWN

// Renders the secondary (peripheral) OLED. The weak default mirrors the master's
// info panels (the state is split-synced); a board overrides it to show its own
// content, e.g. keyball61plus draws the Keyball logo. The master always renders
// the info panels (or bongocat). Only meaningful with OLED + a split keyboard.
void hk_oled_render_secondary(void);

// Sets drag-scroll on both halves at once. Use from a layer hook to put the
// ball(s) into scroll mode while a layer is held (keyball-style: hold the layer,
// the ball scrolls).
void hk_set_dragscroll_both(bool enabled);

// Called once on the master after the split pointing-device presence has been
// negotiated (boards with runtime ball detection only). Lets the keymap reflect
// the detected combination, e.g. into the VIA "Ball availability" layout option.
// Weak default is a no-op.
void hk_pointing_devices_detected_keymap(bool left_has_pointing, bool right_has_pointing);

// #define ENABLE_DRIFT_DETECTION
// #define ENABLE_PIMORONI_ADAPTIVE_MOTION
