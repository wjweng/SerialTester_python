import threading
import time
import serial

from serial_port import SerialPort
from serial_config import SerialConfig


class SerialComm:
    """Serial communication with callback-based events."""

    def __init__(self, config: SerialConfig | None = None, timeout: float = 1,
                 on_error=None, on_rx_char=None, on_break=None):
        self.config = config or SerialConfig()
        self.timeout = timeout
        self.on_error = on_error or (lambda msg: None)
        self.on_rx_char = on_rx_char or (lambda data: None)
        self.on_break = on_break or (lambda: None)
        self._serial: SerialPort | None = None
        self._rx_thread = None
        self._running = threading.Event()
        self._buffer = bytearray()

    def open(self):
        try:
            self._serial = SerialPort(
                port=self.config.port_name,
                baudrate=self.config.baud_rate,
                bytesize=self.config.bytesize,
                parity=self.config.parity,
                stopbits=self.config.stop_bits,
                xonxoff=self.config.flow_control == 'xonxoff',
                rtscts=self.config.flow_control == 'rtscts',
                dsrdtr=self.config.flow_control == 'dsrdtr',
                timeout=self.timeout,
            )
            self._serial.open()
            self._running.set()
            self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
            self._rx_thread.start()
        except Exception as exc:
            self.on_error(str(exc))

    def close(self):
        self._running.clear()
        if self._rx_thread is not None:
            self._rx_thread.join(timeout=1)
            self._rx_thread = None
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def send(self, data: bytes):
        try:
            if self._serial is None:
                raise serial.SerialException('Port not open')
            return self._serial.send(data)
        except Exception as exc:
            self.on_error(str(exc))
            return 0

    def recv(self, size=1) -> bytes:
        try:
            if self._serial is None:
                raise serial.SerialException('Port not open')
            return self._serial.recv(size)
        except Exception as exc:
            self.on_error(str(exc))
            return b''

    def flush(self):
        try:
            if self._serial is not None:
                self._serial.flush()
        except Exception as exc:
            self.on_error(str(exc))

    def ready(self) -> int:
        if self._serial is None:
            return 0
        return self._serial.ready()

    # Internal methods
    def _rx_loop(self):
        while self._running.is_set():
            try:
                waiting = self._serial.ready() if self._serial else 0
                if waiting > 0:
                    data = self._serial.recv(waiting)
                    if data:
                        self._buffer.extend(data)
                        if self._buffer[-1] == 0xFF:  # Check for end of message
                            self.on_rx_char(bytes(self._buffer))
                            self._buffer.clear()
                else:
                    time.sleep(0.01)
            except serial.SerialException as exc:
                if "break" in str(exc).lower():
                    self.on_break()
                else:
                    self.on_error(str(exc))
                break
            except Exception as exc:
                self.on_error(str(exc))
                break
        self._running.clear()