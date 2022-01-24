try:
    import debug

except:
    debug = False

import networking

station = networking.start_sta()

if debug:
    import uftpd
    import utelnetserver

    utelnetserver.start()

import fridge

walkin = fridge.Fridge(watchdog_target_ip=networking.gateway)
walkin.start()
