import machine, onewire, ds18x20, time
import _thread

rtc = machine.RTC()

ENCODING = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
ENCODING_LEN = len(ENCODING)

second_intervals = [3600, 60, 1, 1 / 1_000_000]


def encode_b32(integer, length):
    out = ["0"] * length
    for i in range(0, length):
        mod = integer % ENCODING_LEN
        out[i] = ENCODING[mod]
        integer = (integer - mod) // ENCODING_LEN
        if integer == 0:
            break
    return "".join(out)


get_time = rtc.datetime


class Fridge:
    def __init__(self, compressor_pin=18, onewire_pin=19):
        self.dx = ds18x20.DS18X20(onewire.OneWire(machine.Pin(onewire_pin)))
        self.compressor = machine.Pin(compressor_pin, machine.Pin.OUT)
        self.sensor_uuids = self.dx.scan()
        self.pretty_sensor_uuids = [
            encode_b32(int.from_bytes(s, "little"), 12) for s in self.sensor_uuids
        ]
        self.last = {}
        self.deriv = {}
        self.thread = None
        self.bottom_temp = 2
        self.GRATE_SENSOR = "818VH3RT10FA"
        self.ROOM_SENSOR = "81QJH3RT10FA"
        self.EXHAUST_SENSOR = "8158P3RTZ7FA"
        self.EXIT = False
        self.TICK_TIME = 60

    def measure(self):
        self.dx.convert_temp()
        time.sleep(0.1)
        data = {
            self.pretty_sensor_uuids[i]: self.dx.read_temp(s)
            for (i, s) in enumerate(self.sensor_uuids)
        }
        data["timestamp"] = get_time()
        return data

    def tick(self):
        if not self.last:
            # flush state
            self.measure()
            # update readings
            self.last = self.measure()
            time.sleep(self.TICK_TIME)
        now = self.measure()
        for v in self.last:
            if v != "timestamp":
                self.deriv[v] = self.last.get(v) - now.get(v)
        dt_timedatestamp = [
            a - b for a, b in zip(now["timestamp"], self.last["timestamp"])
        ]
        #  {'81QJH3RT10FA': 13.125, '818VH3RT10FA': 8.25, '8158P3RTZ7FA': 20.625, 'timestamp': (2021, 5, 11, 1, 8, 7, 24, 614094)}
        dt_seconds = sum(
            (
                dt_x * dt_units
                for dt_x, dt_units in zip(dt_timedatestamp[-4:], second_intervals)
            )
        )
        self.deriv["timestamp"] = dt_seconds
        self.last = now
        self.set_compressor()
        return self.deriv

    def set_compressor(self):
        if self.last.get(self.GRATE_SENSOR) < self.bottom_temp:
            self.compressor.off()
        else:
            self.compressor.on()
        return self.compressor.value()

    def run_controller(self):
        while not self.EXIT:
            self.tick()
            time.sleep(self.TICK_TIME)
        self.thread = None

    def stop(self):
        self.EXIT = True

    def start(self):
        self.EXIT = False
        if self.thread == None:
            self.thread = _thread.start_new_thread(self.run_controller, ())
