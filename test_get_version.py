import argparse
import time

from serial_comm import SerialComm
from serial_config import SerialConfig

# Version request packet from original C# GetVersion()
VERSION_CMD = bytes([0x81, 0x09, 0x00, 0x02, 0xFF])


def main() -> None:
    parser = argparse.ArgumentParser(description="Send GetVersion command over serial")
    parser.add_argument("port", help="Serial port name, e.g. COM3 or /dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=9600, help="Baud rate")
    parser.add_argument("--timeout", type=float, default=1.0, help="Read timeout in seconds")
    args = parser.parse_args()

    cfg = SerialConfig(port_name=args.port, baud_rate=args.baud)
    response = bytearray()

    def on_rx(data: bytes) -> None:
        response.extend(data)

    def on_error(msg: str) -> None:
        print("ERROR:", msg)

    comm = SerialComm(config=cfg, timeout=args.timeout, on_rx_char=on_rx, on_error=on_error)
    comm.open()

    try:
        comm.send(VERSION_CMD)
        end = time.time() + args.timeout
        while time.time() < end and (0xFF not in response):
            time.sleep(0.01)
    finally:
        comm.close()

    if response:
        print("Received:", response.hex(" "))
    else:
        print("No response")


if __name__ == "__main__":
    main()
