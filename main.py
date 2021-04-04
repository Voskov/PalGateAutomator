import bluetooth as bt
import requests
import yaml

TOKEN_NAME = 'x-bt-user-token'
INTERVAL = 5


class PalGateAutomator:
    def __init__(self, gate_name: str = None):
        self.gate_name = gate_name
        self.gate_id = self.get_key(gate_name)
        self.token = self.get_key('token')
        self.authorized_devices = self.get_authorized_devices()
        self.authorized_macs = set(self.authorized_devices.keys())

    def main(self):
        while True:
            devices = bt.discover_devices(duration=INTERVAL, flush_cache=True, lookup_names=True, lookup_class=True)
            macs = [device[0] for device in devices]
            for mac in macs:
                if mac in self.authorized_macs:
                    self.open_gate(self.gate_id, mac)

    def open_gate(self, gate_id: str, mac: str):
        url = f'https://api1.pal-es.com/v1/bt/device/{gate_id}/open-gate?outputNum=1'
        response = requests.get(url, headers={TOKEN_NAME: self.token})
        if response.status_code != 200 or response.json()['msg'] != 'Gate opened: true':
            self.handle_error(response)
        else:
            self.log_action(mac)

    def handle_error(self, response: requests.Response):
        pass

    def log_action(self, mac):
        device_name = self.authorized_devices[mac]
        print(f'opened {self.gate_name} for {device_name}')

    @staticmethod
    def get_key(key: str):
        with open('keys.yaml') as keys_file:
            keys = yaml.load(keys_file)
            if key == 'token':
                return keys['token']
            else:
                return keys['gates'][key]

    @staticmethod
    def get_authorized_devices():
        with open('authorized_devices.yaml') as authorized_devices:
            return yaml.load(authorized_devices)


if '__main__' == __name__:
    pga = PalGateAutomator('upper')
    pga.main()
