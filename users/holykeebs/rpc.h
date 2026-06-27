#pragma once

#include <stdint.h>
#include <stdbool.h>

void hk_rpc_sync_state(uint8_t in_buflen, const void* in_data, uint8_t out_buflen, void* out_data);

// Payload for the peripheral->master pointing-device presence query
// (HK_GET_POINTING_INFO transaction), used by runtime ball detection.
typedef struct {
    bool have_pointing;
} hk_pointing_info_t;

void hk_rpc_get_pointing_info(uint8_t in_buflen, const void* in_data, uint8_t out_buflen, void* out_data);
