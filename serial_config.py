import json
import os
from dataclasses import dataclass, asdict

@dataclass
class SerialConfig:
    """Serial port configuration settings."""
    port_name: str = 'COM1'
    baud_rate: int = 38400
    bytesize: int = 8
    parity: str = 'N'
    stop_bits: float = 1
    flow_control: str = 'none'  # 'none', 'rtscts', 'dsrdtr', 'xonxoff'

    def load(self, path: str) -> None:
        """Load configuration from a JSON file if it exists."""
        if not os.path.exists(path):
            return
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        self.port_name = data.get('port_name', self.port_name)
        self.baud_rate = data.get('baud_rate', self.baud_rate)
        self.bytesize = data.get('bytesize', self.bytesize)
        self.parity = data.get('parity', self.parity)
        self.stop_bits = data.get('stop_bits', self.stop_bits)
        self.flow_control = data.get('flow_control', self.flow_control)

    def save(self, path: str) -> None:
        """Save configuration to a JSON file."""
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(asdict(self), fh, indent=2)
