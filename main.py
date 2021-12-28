try:
    import debug

    try:
        DEBUG_ALLOWED = debug.allowed
    except:
        msg = "ATTN: debug.py exists, but debug.allowed not defined!"
        print(msg)
        DEBUG_ALLOWED = False
except:
    DEBUG_ALLOWED = False

import networking

station = networking.start_sta()

if DEBUG_ALLOWED:
    import uftpd
    import utelnetserver
    utelnetserver.start()

import fridge

walkin = fridge.Fridge()
walkin.bottom_temp=0
walkin.TICK_TIME=10
walkin.start()
