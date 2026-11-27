import atexit
import fcntl
from pathlib import Path
import re
import subprocess

import cv2
import numpy as np


WIDTH, HEIGHT = 640, 480
GROUPS_PER_ROW = 26
FRAME_LENGTH = HEIGHT * GROUPS_PER_ROW * 32
BYTE_OFFSETS, BIT_SHIFTS = divmod(np.arange(25, dtype=np.uint16) * 10, 8)


def command(*args):
    return subprocess.check_output(args, text=True, timeout=5)


class IPU3Reader:
    """Read the Surface Laptop 1 OV7251 via the CIO2 capture node."""

    def __init__(self, device, lock_dir, use_strobe=False):
        self.device = Path(device).resolve(strict=True)
        self.media = None
        self.pad = None
        self.enabled_link = None
        self.original_pad = None
        self.original_format = None
        self.original_controls = None
        self.sensor = None
        self.process = None
        self.use_strobe = use_strobe
        self.lock = (Path(lock_dir) / "camera.lock").open("a")
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._start()
        except BaseException:
            self.release()
            raise
        atexit.register(self.release)

    def _start(self):
        for media in sorted(Path("/dev").glob("media[0-9]*")):
            topology = command("media-ctl", "-d", media, "-p")
            capture = re.search(
                r'^- entity \d+: ipu3-cio2 (\d+) \([^\n]+\n[^\n]*\n'
                rf'\s*device node name {re.escape(str(self.device))}\s*$',
                topology, re.MULTILINE,
            )
            if capture:
                self.media = media
                break
        else:
            raise RuntimeError("OV7251 receiver not found")
        port = f"ipu3-csi2 {capture.group(1)}"
        self.pad = f'"{port}":0'
        receiver = re.search(rf'^- entity \d+: {port} \([^\n]+\n(.*?)(?=^- entity|\Z)',
                             topology, re.MULTILINE | re.DOTALL)
        link = re.search(r'<- "(ov7251 [^"]+)":0 \[([^\]]*)\]', receiver.group(1)) if receiver else None
        if not link:
            raise RuntimeError("The OV7251 is not linked to the media controller")
        self.sensor = command("media-ctl", "-d", self.media, "-e", link.group(1)).strip()

        pad = command("media-ctl", "-d", self.media, "--get-v4l2", self.pad)
        self.original_pad = re.search(r"\[stream:0 (fmt:[^\]]+)\]", pad).group(1)
        fmt = command("v4l2-ctl", "-d", self.device, "--get-fmt-video")
        width, height = re.search(r"Width/Height\s*:\s*(\d+)/(\d+)", fmt).groups()
        fourcc = re.search(r"Pixel Format\s*:\s*'([^']+)'", fmt).group(1)
        self.original_format = f"width={width},height={height},pixelformat={fourcc}"

        if "ENABLED" not in link.group(2):
            connection = f'"{link.group(1)}":0 -> {self.pad}'
            command("media-ctl", "-d", self.media, "-l", f"{connection}[1]")
            self.enabled_link = connection
        command("media-ctl", "-d", self.media, "--set-v4l2", f"{self.pad}[fmt:Y10_1X10/640x480 field:none]")
        active = command("v4l2-ctl", "-d", self.device, "--set-fmt-video=width=640,height=480,pixelformat=ip3y",
                         "--get-fmt-video")
        if not re.search(r"Bytes per Line\s*:\s*832\b", active) or "'ip3y'" not in active:
            raise RuntimeError("Unexpected OV7251 capture format")
        names = "exposure,analogue_gain"
        if self.use_strobe:
            names += ",strobe_output_enable"
        settings = command("v4l2-ctl", "-d", self.sensor, f"--get-ctrl={names}")
        values = dict(re.findall(r"^(\w+):\s*(\d+)", settings, re.MULTILINE))
        self.original_controls = ",".join(f"{key}={values[key]}" for key in names.split(","))
        controls = ("exposure=504,analogue_gain=16,strobe_output_enable=1" if self.use_strobe
                    else "exposure=1000,analogue_gain=64")
        command("v4l2-ctl", "-d", self.sensor, f"--set-ctrl={controls}")
        self.process = subprocess.Popen(
            ["v4l2-ctl", "-d", self.device, "--stream-mmap=4", "--stream-poll", "--stream-to=-"],
            stdout=subprocess.PIPE,
        )

    def grab(self):
        return len(self.process.stdout.read(FRAME_LENGTH)) == FRAME_LENGTH

    def _read_raw(self):
        payload = self.process.stdout.read(FRAME_LENGTH)
        if len(payload) != FRAME_LENGTH:
            return None
        groups = np.frombuffer(payload, dtype=np.uint8).reshape(HEIGHT, GROUPS_PER_ROW, 32)
        pairs = groups[..., BYTE_OFFSETS].astype(np.uint16)
        pairs |= groups[..., BYTE_OFFSETS + 1].astype(np.uint16) << 8
        return ((pairs >> BIT_SHIFTS) & 1023).reshape(HEIGHT, -1)[:, :WIDTH]

    def read(self):
        samples = self._read_raw()
        if samples is None:
            return False, None
        if self.use_strobe:
            next_samples = self._read_raw()
            if next_samples is None:
                return False, None
            if next_samples[::8, ::8].mean() > samples[::8, ::8].mean():
                samples = next_samples
        return True, cv2.rotate(samples, cv2.ROTATE_180)

    def get(self, prop):
        return {cv2.CAP_PROP_FRAME_HEIGHT: HEIGHT, cv2.CAP_PROP_FRAME_WIDTH: WIDTH}.get(prop, 0)

    def release(self):
        if self.lock.closed:
            return
        try:
            if self.process is not None:
                if self.process.poll() is None:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        self.process.wait()
                self.process.stdout.close()
                self.process = None
            try:
                if self.original_controls:
                    command("v4l2-ctl", "-d", self.sensor, f"--set-ctrl={self.original_controls}")
            finally:
                if self.original_format:
                    try:
                        command("media-ctl", "-d", self.media, "--set-v4l2", f"{self.pad}[{self.original_pad}]")
                    finally:
                        try:
                            command("v4l2-ctl", "-d", self.device, f"--set-fmt-video={self.original_format}")
                        finally:
                            if self.enabled_link:
                                command("media-ctl", "-d", self.media, "-l", f"{self.enabled_link}[0]")
        finally:
            self.lock.close()
