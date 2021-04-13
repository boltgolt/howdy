import ctypes
import os

UVCIOC_CTRL_QUERY = 0xC0107521
UVC_SET_CUR = 0x01
UNIT = 0x0e
SELECTOR = 0x0e
QUERY = UVC_SET_CUR
SIZE = 2
LIBC = "libc.so.6"


class uvc_ctrl_query(ctypes.Structure):
    _fields_ = [
        ("unit", ctypes.c_uint8),
        ("selector", ctypes.c_uint8),
        ("query", ctypes.c_uint8),
        ("size", ctypes.c_uint16),
        ("data", ctypes.POINTER(ctypes.c_uint8)),
    ]


u8_array = ctypes.c_uint8 * SIZE
data_maker = lambda v: uvc_ctrl_query(UNIT, SELECTOR, QUERY, SIZE, u8_array.from_buffer(v))


def _set_ir_emitted(device_path: str, data: bytearray):
    fd = os.open(device_path, os.O_WRONLY)
    try:
        ctypes.CDLL(LIBC).ioctl(fd, UVCIOC_CTRL_QUERY, ctypes.byref(data_maker(data)))
    finally:
        os.close(fd)


def ir_emitted_on(device_path: str):
    _set_ir_emitted(device_path, bytearray([0x02, 0x19]))


def ir_emitted_off(device_path: str):
    _set_ir_emitted(device_path, bytearray([0x00, 0x00]))


if __name__ == '__main__':
    ir_emitted_on("/dev/video2")
