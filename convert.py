'''
Proxies Convertor:
This script converts proxies from Subscribe proxy node to port Mapping proxies
single port to multiple ports.

input: subscript url
output: port Mapping ver yaml file

use clash meta to load the yaml file
then you can use proxies by local port
'''

import requests
import yaml
from argparse import ArgumentParser

try:
    from rich import print
except ImportError:
    pass

BLACK_LIST_KEYWORDS = ['剩余流量', '过期时间', '应急节点']

def get_yaml(url):
    resp = requests.get(url)
    if resp.status_code == 200:
        return yaml.load(resp.text, Loader=yaml.FullLoader)
    else:
        return None
def convert_yaml(yaml_data: dict, start_port: int):
    _proxies = yaml_data.get('proxies')
    proxies = [p for p in _proxies if any(k in p.get('name', '') for k in BLACK_LIST_KEYWORDS) == False]
    if proxies is None: raise ValueError('proxies not found in yaml data')
    if len(proxies) + start_port > 65535:
        raise ValueError(f'not enough ports to convert all proxies, should be at least {len(proxies)} more ports')
    print(f'get {len(proxies)} proxies, start port is {start_port}')
    
    hosts = yaml_data.get('hosts')
    dns = yaml_data.get('dns')
    if hosts is None: hosts = {'mtalk.google.com': '108.177.125.188'}
    if dns is None: dns = {
        'enable': True,
        'enhanced-mode': 'fake-ip',
        'fake-ip-range': '198.18.0.1/16',
        'default-nameserver':
            ['114.114.114.114'],
        'nameserver':
            ['https://doh.pub/dns-query']
    }
    if dns.get('listen') is not None:
        port = dns.get('listen').split(':')[-1]
        dns['listen'] = f'127.0.0.1:{int(port)+1}' # change the listen port to avoid conflict with other programs
        
    allow_lan = True if yaml_data.get('allow-lan', False) else False
    
    listeners = []
    c = 0
    curr_port = start_port
    for proxy in proxies:
        proxy: dict
        name = proxy.get('name')
        listeners.append({
            'name': f'mixed{c}',
            'type': 'mixed',
            'port': curr_port,
            'proxy': name,
        })
        c+=1
        curr_port+=1
    
    return {
        'allow-lan': allow_lan,
        'hosts': hosts,
        'dns': dns,
        'listeners': listeners,
        'proxies': proxies
    }

def main():
    parser = ArgumentParser()
    parser.add_argument('-u', '--url', help='subscribe proxy node url')
    parser.add_argument('-p', '--start_port', type=int, help='start port for port mapping proxies')
    args = parser.parse_args()
    url:str = args.url
    start_port:int = args.start_port
    if start_port > 65535 or start_port < 1:
        raise ValueError('start_port should be between 1 and 65535')
    
    yaml_data = get_yaml(url)
    if yaml_data is None:
        print('Failed to get yaml data')
        return
    new_yaml_data = convert_yaml(yaml_data, start_port)
    with open('converted.yaml', 'w') as f:
        yaml.dump(new_yaml_data, f, encoding='utf-8', allow_unicode=True, indent=2, width=2)
    print('Done!')
    
if __name__ == '__main__':
    main()
