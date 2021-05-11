import _thread

import debug
import networking

station = networking.start_sta()

if debug.allowed:
    import uftpd
    import utelnetserver
    from uresetserver import *

    utelnetserver.start()
    start_reset_server()
