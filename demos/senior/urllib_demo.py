import urllib.parse
import urllib.request
from urllib.error import HTTPError
from urllib.robotparser import RobotFileParser

# response = urllib.request.urlopen('https://www.python.org')
# print(response.read().decode('utf-8'))
# print(type(response))

url = 'http://www.neeq.com.cn/nqhqController/nqhq_en.do'
headers = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
    'Host': 'www.neeq.com.cn',
    'Content-Type': 'application/json'
}
data = {
    "keyword": None,
    "status": None
 }
data = bytes(urllib.parse.urlencode(data), encoding='utf8')
request = urllib.request.Request(url,  headers=headers, method='POST')
try:
    response = urllib.request.urlopen(request)
    respstr = str(response.read(), 'utf8')
    print(respstr)
except HTTPError as e:
    content = e.read()
    print(content)
# data = bytes(urllib.parse.urlencode({'word': 'hello'}), encoding='utf8')
# response = urllib.request.urlopen('http://httpbin.org/post', data=data)
# print(response.read())

rp = RobotFileParser()
rp.set_url('http://www.jianshu.com/robots.txt')
rp.read()
print(rp.can_fetch('*', 'http://www.jianshu.com/p/b67554025d7d'))
print(rp.can_fetch('*', "http://www.jianshu.com/search?q=python&page=1&type=collections"))