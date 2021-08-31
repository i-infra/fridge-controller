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

if debug:
    import uftpd
    import utelnetserver
    from uresetserver import *

    utelnetserver.start()
    start_reset_server()

import fridge

walkin = fridge.Fridge()
walkin.bottom_temp=0
walkin.TICK_TIME=10
walkin.start()
