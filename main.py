import bluetooth as bt
import requests
import yaml

TOKEN_NAME = 'x-bt-user-token'


class PalGateAutomator:
    authorized_devices = []

    def __init__(self, gate_name: str = None):
        self.gate_id = self.get_key(gate_name)
        self.token = self.get_key('token')
        self.authorized_macs = [device[0] for device in self.authorized_devices]

    def main(self):
        devices = bt.discover_devices(duration=3, flush_cache=False, lookup_names=True, lookup_class=True)
        macs = [device[0] for device in devices]
        if any(mac in self.authorized_macs for mac in macs):
            self.open_gate(self.gate_id)

    def open_gate(self, gate):
        url = f'https://api1.pal-es.com/v1/bt/device/{gate}/open-gate?outputNum=1'
        response = requests.get(url, headers={TOKEN_NAME: self.token})
        if response.status_code != 200 or response.json()['msg'] != 'Gate opened: true':
            self.handle_error(response)
        else:
            self.log_action()

    def handle_error(self, response: requests.Response):
        pass

    def log_action(self):
        pass

    @staticmethod
    def get_key(key: str):
        with open('keys.yaml') as keys_file:
            keys = yaml.load(keys_file)
            if key == 'token':
                return keys['token']
            else:
                return keys['gates'][key]


if '__main__' == __name__:
    pga = PalGateAutomator('upper')
    pga.main()
