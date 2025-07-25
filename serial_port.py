import serial

class SerialPort:
    """Simple serial port wrapper using pySerial."""
    def __init__(self, port='COM1', baudrate=9600, bytesize=serial.EIGHTBITS,
                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                 xonxoff=False, rtscts=False, dsrdtr=False, timeout=1):
        self.port_name = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.xonxoff = xonxoff
        self.rtscts = rtscts
        self.dsrdtr = dsrdtr
        self.timeout = timeout
        self.ser = None

    def open(self):
        if self.ser is None:
            self.ser = serial.Serial(port=self.port_name,
                                     baudrate=self.baudrate,
                                     bytesize=self.bytesize,
                                     parity=self.parity,
                                     stopbits=self.stopbits,
                                     xonxoff=self.xonxoff,
                                     rtscts=self.rtscts,
                                     dsrdtr=self.dsrdtr,
                                     timeout=self.timeout)
        elif not self.ser.is_open:
            self.ser.open()

    def close(self):
        if self.ser is not None and self.ser.is_open:
            self.ser.close()

    def send(self, data: bytes):
        if self.ser is None or not self.ser.is_open:
            raise serial.SerialException("Port not open")
        return self.ser.write(data)

    def recv(self, size=1) -> bytes:
        if self.ser is None or not self.ser.is_open:
            raise serial.SerialException("Port not open")
        return self.ser.read(size)

    def flush(self):
        if self.ser is None or not self.ser.is_open:
            raise serial.SerialException("Port not open")
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def ready(self) -> int:
        if self.ser is None or not self.ser.is_open:
            return 0
        return self.ser.in_waiting
