import csv
with open('Z:/1_个人文件夹/haozhenjie/2020-04/test.csv', 'w', newline='') as csvfile:
    fieldnames = ['dfdsrmc', 'title', 'xylx', 'clhj', 'clr', 'ddsj', 'fcsj']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writerow({'dfdsrmc': '对方当事人名称', 'title': '标题', 'xylx': '协议类型', 'clhj': '处理环节', 'clr': '处理人', 'ddsj': '到达时间', 'fcsj': '发出时间'})
