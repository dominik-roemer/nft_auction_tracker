import requests
r = requests.get('https://httpbin.org/get').json()
print(r)