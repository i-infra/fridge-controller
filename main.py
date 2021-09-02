try:
    import debug

except:
    debug = False

import networking

if debug:
    import uftpd
    import utelnetserver
    from uresetserver import *

    utelnetserver.start()
    start_reset_server()

import fridge

walkin = fridge.Fridge(watchdog_target_ip=networking.gateway)
walkin.start()
