import requests

r = requests.get('http://www.gtja.net/wps/myportal')
print(type(r))
print(r.status_code)
print(type(r.text))
#text = str(r.text, 'utf8')
print(r.text)
print(r.cookies)