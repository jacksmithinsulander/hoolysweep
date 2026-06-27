# Build Options
BOOTMAGIC_ENABLE = no       # Enable Bootmagic Lite
EXTRAKEY_ENABLE = yes       # Audio control and System control
CONSOLE_ENABLE = no         # Console for debug
COMMAND_ENABLE = no         # Commands for debug and configuration
NKRO_ENABLE = no            # Enable N-Key Rollover
BACKLIGHT_ENABLE = no       # Enable keyboard backlight functionality
AUDIO_ENABLE = no           # Audio output

# Duplex matrix. Private copy under lib/ so the released keyball61 (which keeps
# its own copy under keyboards/keyball/lib) is unaffected by changes here.
CUSTOM_MATRIX = lite
SRC += lib/duplexmatrix/duplexmatrix.c

# Split keyboard.
SERIAL_DRIVER = vendor

# PMW3360 optical trackball sensor. (Pointing + serial config will move to the
# holykeebs userspace once it gains a PMW3360 device kind.)
POINTING_DEVICE_ENABLE = yes
POINTING_DEVICE_DRIVER = pmw3360

MOUSEKEY_ENABLE = yes

# Rotary encoder (one per side, declared in keyboard.json).
ENCODER_MAP_ENABLE = yes

# Per-key RGB lighting. Enable per keymap.
RGB_MATRIX_ENABLE = no
RGB_MATRIX_DRIVER = ws2812

# Do not enable SLEEP_LED_ENABLE. it uses the same timer as BACKLIGHT_ENABLE
SLEEP_LED_ENABLE = no       # Breathing sleep LED during USB suspend

# OLED is provided by the holykeebs userspace (enable with OLED=yes).
OLED_ENABLE = no

# Disable other features to squeeze firmware size
SPACE_CADET_ENABLE = no
MAGIC_ENABLE = no
