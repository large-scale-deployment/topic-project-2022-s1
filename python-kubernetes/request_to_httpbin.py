import requests

headers = {'X-Forwarded-For':'127.0.0.127,192.168.1.1,192.168.1.2'}
res = requests.get('http://172.18.0.2:31691/get', headers=headers)
print(res.content.decode('utf-8'))
