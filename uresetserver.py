import socket
import machine
import uhashlib
import _thread
import time

ENCODING = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
ENCODING_LEN = len(ENCODING)


def encode_b32(integer, length):
    out = ["0"] * length
    for i in range(0, length):
        mod = integer % ENCODING_LEN
        out[i] = ENCODING[mod]
        integer = (integer - mod) // ENCODING_LEN
        if integer == 0:
            break
    return "".join(out)


RAW_MACHINE_UID = machine.unique_id()
SALT = b"SALT FOR ADDED SECURITY"


MACHINE_UID = int.from_bytes(uhashlib.sha256(RAW_MACHINE_UID + SALT).digest(), "little")
MACHINE_STR = encode_b32(MACHINE_UID, 16)


def reset_in(seconds):
    time.sleep(seconds)
    machine.reset()


def wait_for_magic():
    # (R)ESET = 3537
    addr = socket.getaddrinfo("0.0.0.0", 3537)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print("listening for RESET (" + MACHINE_STR + ") on 3537", addr)

    while True:
        cl, addr = s.accept()
        cl_file = cl.makefile("rwb", 0)
        while True:
            line = cl_file.readline()
            if not line or line == b"\r\n":
                break
            line_str = line.decode().strip()
            if line_str == MACHINE_STR:
                _thread.start_new_thread(reset_in, (10,))
                cl_file.write(b"RESETTING! (10s)\r\n")
            else:
                time.sleep(0.1)
                cl_file.write(b"NO.\r\n")


global RESET_SERVER_THREAD


def start_reset_server():
    global RESET_SERVER_THREAD
    RESET_SERVER_THREAD = _thread.start_new_thread(wait_for_magic, ())
