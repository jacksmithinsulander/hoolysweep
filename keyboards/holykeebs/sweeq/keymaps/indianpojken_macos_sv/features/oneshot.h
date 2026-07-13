#pragma once

#include QMK_KEYBOARD_H

typedef enum {
    os_up_unqueued,
    os_up_queued,
    os_down_unused,
    os_down_used,
} oneshot_state;

void update_oneshot(
    oneshot_state *state,
    uint16_t mod,
    uint16_t trigger,
    uint16_t keycode,
    keyrecord_t *record
);

bool is_oneshot_cancel_key(uint16_t keycode);
bool is_oneshot_ignored_key(uint16_t keycode);
