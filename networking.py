import network
import ntptime
import machine
import time

rtc = machine.RTC()
import known_APs

sta_if = network.WLAN(network.STA_IF)

def start_sta():
    sta_if.active(True)

    APs = sta_if.scan()
    AP_names = [x[0] for x in APs]
    print(AP_names)
    for AP_name in AP_names:
        if AP_name in known_APs.known_APs:
            sta_if.connect(AP_name, known_APs.known_APs[AP_name], listen_interval=-1)
            break

    connect_attempt_count = 100
    while (connect_attempt_count > 0) and not sta_if.isconnected():
        time.sleep(0.1)
        connect_attempt_count -= 1
    if connect_attempt_count <= 0:
        print("connect failed")
        sta_if.active(False)
        return False
    else:
        my_ip = sta_if.ifconfig()[0]
        try:
            time.sleep(1)
            ntptime.settime()
            print("current time: " + str(rtc.datetime()))
        except Exception:
            print("failed to set time")
        return sta_if

