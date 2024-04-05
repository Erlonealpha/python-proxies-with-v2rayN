import requests
# from rich import print
import json

proxies = {
    'http': 'http://127.0.0.1:42090',
    'https': 'http://127.0.0.1:42090'
}

def test_proxy_and_get_ip(proxies):
    url = 'https://httpbin.org/ip'
    try:
        response = requests.get(url, proxies=proxies)
    except requests.exceptions.ProxyError:
        print(f'[red]Proxy {proxies} is not available.[/red]')
        quit(0)
    return response.json()['origin']
def test_proxy_and_get_ip_and_info(proxies):
    ip = test_proxy_and_get_ip(proxies)
    url = f'http://ip-api.com/json/{ip}?lang=zh-CN'
    resp = requests.get(url, proxies=proxies)
    return resp.json()
    
if __name__ == '__main__':
    jsondata = test_proxy_and_get_ip_and_info(proxies)
    print(json.dumps(jsondata, indent=2, ensure_ascii=False))
    print()