import datetime
import uuid
from concurrent.futures import ThreadPoolExecutor

import requests
from pyquery import PyQuery as pq

from demos.datamatrix.education.model.schoolmodel import School, DBSession

shanghai = '9'

youeryuan = '1'
xiaoxue = '2'
chuzhong = '3'


def get_school_urls_by_city(cityno):
    def fn(link):
        return link.attr('href')
    cityurl = 'https://www.ruyile.com/xuexiao/?a={}'.format(cityno)
    response = requests.get(url=cityurl)
    htmlstr = response.text
    htmlobj = pq(htmlstr)
    links = htmlobj('div.qylb:gt(0) a').items()
    r = map(fn, links)
    return list(r)


def get_total_pages(url, typeno):
    page_url = url + '&t=' + typeno
    response = requests.get(url=page_url)
    htmlstr = response.text
    htmlobj = pq(htmlstr)
    page_a = htmlobj('div.fy a:last')
    max_page_url = page_a.attr('href')
    if max_page_url is not None:
        lastidx = max_page_url.rindex('=')
        return int(max_page_url[lastidx+1:])
    else:
        return 0


def get_school_detail(schoolurl, typeno):
    def parse_txt(str):
        return str.split('：')[1].strip()
    school = {
        "name": '',
        "area": '',
        "level": '',
        "type": '',
        "address": '',
        "edu_type": '',
        'info': ''
    }
    response = requests.get(url=schoolurl)
    htmlstr = response.text
    htmlobj = pq(htmlstr)
    header_div = htmlobj('div.header')
    school['name'] = header_div.children().eq(0).text()
    outer_div = htmlobj('div.stq')
    props_div = outer_div.find('div.xxsx')
    #print(infos.html())
    for prop in props_div.children().items():
        propname = prop.find('strong').text()
        if propname == '所属地区':
            school['area'] = prop.find('a').eq(1).html()
        if propname == '学校性质':
            school['edu_type'] = parse_txt(prop.text())
        if propname == '学校级别':
            school['level'] = parse_txt(prop.text())
        if typeno == xiaoxue:
            school['type'] = '小学'
        elif typeno == youeryuan:
            school['type'] = '幼儿园'
        elif typeno == chuzhong:
            school['type'] = '初中'
        if propname == '学校地址':
            school['address'] = parse_txt(prop.text())
    intro_div = outer_div.find('div.jj>p')
    school['info'] = intro_div.text()
    school['id'] = ''.join(str(uuid.uuid4()).split('-'))
    school['data_year'] = datetime.datetime.now().strftime("%Y%m%d")
    return School(id=school['id'], data_year=school['data_year'], name=school['name'], area=school['area'], level=school['level'], type=school['type'], address=school['address'], edu_type=school['edu_type'], info=school['info'])


def add_school(new_school):
    # 创建session对象:
    session = DBSession()
    # 添加到session:
    session.add(new_school)
    # 提交即保存到数据库:
    session.commit()
    # 关闭session:
    session.close()


def get_school_urls_by_page(city_url, typeno, pageno):
    def fn(link):
        return link.attr('href')
    page_url = '{}&t={}&p={}'.format(city_url, typeno, pageno)
    print(page_url)
    response = requests.get(url=page_url)
    htmlstr = response.text
    htmlobj = pq(htmlstr)
    header_divs = htmlobj('div.sk a').items()
    r = map(fn, header_divs)
    return list(set(r))


def pull_schools(cityno, typeno):
    def get_and_insert(school_url, typeno):
        schoolobj = get_school_detail(school_url, typeno)
        try:
            add_school(schoolobj)
        except:
            print(schoolobj)

    city_urls = get_school_urls_by_city(cityno)
    thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="school_")
    for city_url in city_urls:
        max_page = get_total_pages(city_url, typeno)
        for i in range(1, max_page+1):
            school_urls = get_school_urls_by_page(city_url, typeno, i)
            for school_url in school_urls:
                thread_pool.submit(get_and_insert, school_url, typeno)

    thread_pool.shutdown(wait=True)


if __name__ == '__main__':
    cityno = shanghai
    typeno = chuzhong
    pull_schools(cityno, typeno)