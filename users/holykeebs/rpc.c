#include "rpc.h"
#include "pointing.h"
#include "pointing_device.h"
#include "hk_debug.h"

void hk_rpc_sync_state(uint8_t in_buflen, const void* in_data, uint8_t out_buflen, void* out_data) {
    const hk_state_t *incoming_state = (const hk_state_t*)in_data;

    printf("hk_rpc_sync_state: got state incoming_state->is_main_side: %u\n", incoming_state->is_main_side);
    if (!incoming_state->is_main_side) {
        printf("hk_rpc_sync_state: invalid state, ignoring\n");
        return;
    } else {
        g_hk_state = *incoming_state;
        g_hk_state.is_main_side = false;
        debug_hk_state_to_console(&g_hk_state);
    }
}

// Runs on the peripheral: report whether this half has a working pointing device.
// In a combined split, pointing_device_get_status() reflects the local sensor.
void hk_rpc_get_pointing_info(uint8_t in_buflen, const void* in_data, uint8_t out_buflen, void* out_data) {
    hk_pointing_info_t info = {
        .have_pointing = pointing_device_get_status() == POINTING_DEVICE_STATUS_SUCCESS,
    };
    *(hk_pointing_info_t*)out_data = info;
}
