import argparse
from pathlib import Path
import yaml
import requests
import bluetooth as bt

TOKEN_NAME = 'x-bt-user-token'
INTERVAL = 5


class PalGateAutomator:
    def __init__(self):
        self.gate_name = self.get_key('active_gate')
        self.gate_id = self.get_key(self.gate_name)
        self.token = self.get_key('token')
        self.authorized_devices = self.get_authorized_devices()
        self.authorized_macs = set(self.authorized_devices.keys())

    def main(self):
        print(f'Starting service for {self.gate_name}')
        while True:
            devices = bt.discover_devices(duration=INTERVAL, flush_cache=True, lookup_names=True, lookup_class=True)
            macs = [device[0] for device in devices]
            for mac in macs:
                if mac in self.authorized_macs:
                    self.open_gate(self.gate_id, mac)

    def open_gate(self, gate_id: str, mac: str):
        url = f'https://api1.pal-es.com/v1/bt/device/{gate_id}/open-gate?outputNum=1'
        response = requests.get(url, headers={TOKEN_NAME: self.token})
        if response.status_code == 200 and response.json()['msg'] == 'Gate opened: true':
            self.log_action(mac)

    def log_action(self, mac):
        device_name = self.authorized_devices[mac]
        print(f'opened {self.gate_name} for {device_name}')

    @staticmethod
    def get_key(key: str):
        with open(Path(__file__).parent / 'keys.yaml') as keys_file:
            keys = yaml.safe_load(keys_file)
            if key == 'token':
                return keys['token']
            elif key == 'active_gate':
                return keys['active_gate']
            else:
                return keys['gates'][key]

    def get_authorized_devices(self):
        with open(Path(__file__).parent / 'authorized_devices.yaml') as authorized_devices:
            return yaml.safe_load(authorized_devices)[self.gate_name]


if __name__ == '__main__':
    pga = PalGateAutomator()
    pga.main()
