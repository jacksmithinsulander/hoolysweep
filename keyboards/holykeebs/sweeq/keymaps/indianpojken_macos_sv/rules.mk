COMBO_ENABLE = yes
VPATH += keyboards/gboards

SRC += features/oneshot.c
SRC += features/tabber.c
SRC += features/macro.c
SRC += features/magic_caps.c
SRC += features/oneshot_fn.c

REPEAT_KEY_ENABLE = yes
KEY_OVERRIDE_ENABLE = yes
CAPS_WORD_ENABLE = yes
MOUSEKEY_ENABLE = yes

RGBLIGHT_ENABLE = no
RGB_MATRIX_ENABLE = no
