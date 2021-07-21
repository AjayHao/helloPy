from urllib.parse import urlencode

import requests


def test():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'Content-Type': 'text/html;charset=UTF-8'
    }

    url = 'http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do'

    param = {
        "aoData": [
                  # {"name":"sEcho","value":1},
                  # {"name":"iColumns","value":6},
                  # {"name":"sColumns","value":",,,,,"},
                   {"name":"iDisplayStart","value":0},
                   {"name":"iDisplayLength","value":20},
                  # {"name":"mDataProp_0","value":"fundCode"},{"name":"mDataProp_1","value":"fundId"},{"name":"mDataProp_2","value":"reportName"},{"name":"mDataProp_3","value":"organName"},{"name":"mDataProp_4","value":"reportDesp"},{"name":"mDataProp_5","value":"reportSendDate"},
                  # {"name":"fundType","value":""},
                   {"name":"reportType","value":"FC"},
                  # {"name":"reportYear","value":""},
                  # {"name":"fundCompanyShortName","value":""},
                  # {"name":"fundCode","value":""},
                  # {"name":"fundShortName","value":""},
 {"name":"startUploadDate","value":"2019-09-28"},{"name":"endUploadDate","value":"2020-09-27"}]
    }

    #paramstr = urlencode(param).replace("%27", "%22")  可以通过加encoding的方式处理%27与%22的问题
    paramstr = urlencode(param).replace("%27", "%22")
    get_url = url + '?' + paramstr + '&_=1123123132132'
    print(get_url)
    response = requests.get(url=get_url, headers=headers)
    if response.status_code == 200:
        # test
        #write_file(fullpath=output_path+'列表返回结果.json', text=response.text)
        return response.json()
    return None



# 主程序调用
if __name__ == '__main__':
    obj = test()
    print(obj)
