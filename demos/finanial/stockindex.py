#!/usr/bin/python3

import easyquotation
import tushare as ts

quotation = easyquotation.use('sina') # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
# 单只股票
data1 = quotation.real('162411') # 支持直接指定前缀，如 'sh000001'
# 多只股票
quotation.stocks(['000001', '162411'])
print(type(data1))
print(data1)


data2 = ts.get_hist_data('600848') #一次性获取全部数据
print(type(data2))
print(data2)