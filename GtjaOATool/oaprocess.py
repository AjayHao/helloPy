from urllib.parse import urlencode
from pyquery import PyQuery as pq
from tkinter import ttk
from tkinter import messagebox
from tkinter import *
import datetime
import time
import requests
import csv

version_line = '\n\n-----------------------------\n'
version_desc_arr = [
    "V0.1.0 - 20200408: 导出列表增加“对方当事人名称”",
    "V0.2.0 - 20200414: 导出列表”协议类型“，且筛选过滤'聘请律师协议', '人民币同业存款协议', '外聘服务协议', '银行结算帐户管理协议'四种协议"
]

# 外部传入参数
mainframe = None
begin_date_sv = None
end_date_sv = None
session_id_sv = None
output_path_sv = None
canvas = None
process_sv = None
button = None
output_path = ''
ltpa_token_string = ''
file_type = 'OA006'  #OA006-合同协议 OA012-印章申请
file_name = 'OA流程跟踪数据拉取结果【合同协议】.csv'
oa_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Host': 'oa.gtja.net'
}
EXCEPT_LIST = ['聘请律师协议', '人民币同业存款协议', '外聘服务协议', '银行结算帐户管理协议']


CANVAS_LENGTH = 600
PAGE_SIZE = 100


# 分页取数
def get_contract_list_by_page(page_no):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    url = 'https://link.gtja.net/link/common/oa/ajaxMappingHandler'

    post_param = {
        "data": {
            "Param": {
                "begindate": begin_date_sv.get().strip(),
                "enddate": end_date_sv.get().strip(),
                "fileclass_main": "OA",
                "fileclass": file_type,
                "requester": "1"
            },
            "Type": "OA_TRANS_Q9902",
            "Page": {
                "CurrentPage": page_no,
                "PageSize": PAGE_SIZE
            },
            "ColOrder": {
                "ColName": "",
                "Sort": 0
            }
        }
    }

    url_param = {
        "sysId": 1,
        "funId": "OA_TRANS_Q9902",
        "oem.sessionid": session_id_sv.get().strip(),
        "t": time.time
    }

    post_data = urlencode(post_param)
    post_url = url + '?' + urlencode(url_param)
    print(post_url)
    response = requests.post(url=post_url, data=post_data, headers=headers)
    if response.status_code == 200:
        # test
        #write_file(fullpath=output_path+'列表返回结果.json', text=response.text)
        return response.json()
    return None


# 抓取合同协议列表
def get_contract_list():
    total_list = []
    resp = get_contract_list_by_page(1)
    page_info = resp['Page']
    #total_records = page_info['Records']
    total_page = page_info['TotalPage']
    for page in range(1, total_page+1):
        resp = get_contract_list_by_page(page)
        batch_data = resp['Data']
        if batch_data is not None and len(batch_data) > 0:
            total_list = total_list + batch_data

    return total_list


# 抓取合同详情
def get_contract_detail(detail_obj):
    contract_detail = {'dfdsrmc': ''}  # 对方当事人全称
    open_url = detail_obj['TODOURL'].replace("editdocument", "opendocument")
    cookies = {'LtpaToken': ltpa_token_string}
    # 填抓包内容
    # r.cookies.update(c)  # 更新cookies
    response = requests.get(url=open_url, cookies=cookies, headers=oa_headers)
    response.encoding = 'gbk'
    htmlstr = response.text
    # 需要输出详情
    #if is_detail_output:
    #    write_file(output_path + '【合同协议详情】-' + detail_obj['TODOTITLE'] +".html", htmlstr)
    # 解析详情html
    htmlobj = pq(htmlstr)
    tds = htmlobj('table.tableForm:eq(2) tr td').items()
    for td in tds:
        if td.text() == '协议类型':
            contract_detail['xylx'] = td.next().remove('span').text()

        # 因对方当事人名称字段可能被页面吞掉，改为td:合同金额往前追溯
        if td.text() == '合同金额':
            contract_detail['dfdsrmc'] = td.parent().prev().find('td.Title').next().text().strip()
            break
    return contract_detail


# 抓取跟踪信息
def get_process_track(detail_obj, contract_detail):
    docid = detail_obj['TODONO']
    url = detail_obj['TODOURL']
    sidx = url.find('nsf')
    track_prefix = url[0:sidx]
    open_url = track_prefix+'nsf/TraceDoc?OpenAgent&Time='+str(time.time)+'&DocID='+docid
    cookies = {'LtpaToken': ltpa_token_string}
    response = requests.get(url=open_url, cookies=cookies, headers=oa_headers)
    response.encoding = 'gbk'
    htmlstr = response.text

    track_list = []
    # 解析详情html
    htmlobj = pq(htmlstr)
    trs = htmlobj('table.docoumentTable tr:gt(0)').items()
    for tr in trs:
        tds = tr.children()
        track_list.append({
            'dfdsrmc': contract_detail['dfdsrmc'],
            'title': detail_obj['TODOTITLE'],
            'xylx': contract_detail['xylx'],
            'clhj': pq(tds[0]).text(),
            'clr': pq(tds[1]).text(),
            'ddsj': pq(tds[2]).text(),
            'fcsj': pq(tds[3]).text()
        })

    # test
    # write_file('C:\\Users\\AjayHao\\Desktop\\contract\\track_list.json', str(track_list))
    # print(str(track_list))
    return track_list


# 输出中间结果（调试用）
def write_file(path, text):
    decoded_path = path.replace("\t", " ").replace("\x06", "").replace("\x05", "").replace("\x07", "")
    f = open(file=decoded_path, mode='w', encoding='gbk')
    f.write(text)
    # 关闭打开的文件
    f.close()


# 导出excel表头
def export_csv_header():
    with open(output_path + file_name, 'w', newline='') as csvfile:
        fieldnames = ['dfdsrmc', 'title', 'xylx', 'clhj', 'clr', 'ddsj', 'fcsj']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'dfdsrmc': '对方当事人名称', 'title': '标题', 'xylx': '协议类型', 'clhj': '处理环节', 'clr': '处理人', 'ddsj': '到达时间', 'fcsj': '发出时间'})


# 导出excel
def export_csv_content(data_list):
    with open(output_path + file_name, 'a', newline='') as csvfile:
        fieldnames = ['dfdsrmc', 'title', 'xylx', 'clhj', 'clr', 'ddsj', 'fcsj']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for item in data_list:
            writer.writerow(item)


# 执行爬数主逻辑
def execute():
    global ltpa_token_string
    global output_path

    # 参数校验
    if begin_date_sv.get() == '' or \
            end_date_sv.get() == '' or \
            session_id_sv.get() == '' or \
            output_path_sv.get() == '' or \
            ltpa_token_text.get(0.0, "end").replace('\n', '') == '':
        messagebox.showwarning("执行失败","解析异常：输入项未填写完整")
        return

    try:
        button.state(["disabled"])
        # 先重置进度条
        reset_progress()
        # 参数解析
        ltpa_token_string = ltpa_token_text.get(0.0, "end").strip().replace('\n', '').replace('\r', '')
        output_path = output_path_sv.get()
        if not output_path.endswith('/') and not output_path.endswith('\\'):
            output_path = output_path + '/'
            # 查询文件类型

        # 获得申请列表
        contract_list = get_contract_list()

        # 需要对excel去重
        #excel_dict = {}
        export_csv_header()
        idx = 0
        total = len(contract_list)
        while idx < total:
            item = contract_list[idx]
            contract_detail = get_contract_detail(item)
            # 判断是否需要排除的协议类型
            if contract_detail['xylx'] not in EXCEPT_LIST:
                track_list = get_process_track(item, contract_detail)
                refresh_progress(idx+1, total, item['TODOTITLE'])
                export_csv_content(track_list)
            idx += 1
        # test
        #write_file(output_path + 'finalData.json', str(excel_list))
        # 输出excel
        #excel_list = list(excel_dict.values())
        messagebox.showinfo("执行完毕", "解析完毕，请到下载目录查看结果")
    finally:
        button.state(["!disabled"])


# 版本信息
def show_version_info():
    messagebox.showinfo("版本信息", "Version：     V0.1.1\nDeveloper： Ajay Hao\n\n更新日志: \n" + version_line.join(version_desc_arr))

########  UI
# 绘制菜单
def draw_menu(root):
    menubar = Menu(root)
    menubar.add_command(label='版本信息', command=show_version_info)
    root.config(menu=menubar)


# 绘制组件
def draw_frame(root):
    global mainframe
    global begin_date_sv
    global end_date_sv
    global session_id_sv
    global ltpa_token_text
    global output_path_sv
    global canvas
    global process_sv
    global button
    begin_date_sv = StringVar()
    end_date_sv = StringVar()
    session_id_sv = StringVar()
    output_path_sv = StringVar()
    process_sv = StringVar()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    mainframe = Frame(root) #bg='black'
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    # 组件
    readme = Label(mainframe, bg='white', text='操作说明：参数均为必填项，其中oem.sessionid与LtpaToken通过以下方式获取：使用特定人员账号在Chrome浏览器上登录OA，并点击个人工作台。等待办展现后，按下F12，选Application标签页，点开左侧Storage->Cookies->https://link.gtja.net，找到这两个名称对应的值(Value)拷贝出即可', anchor='center', wraplength=780, justify='left')
    begin_date_label = Label(mainframe, text='开始日期(yyyyMMdd):', justify='right')
    end_date_label = Label(mainframe, text='结束日期(yyyyMMdd):', justify='right')
    begin_date_entry = ttk.Entry(mainframe, textvariable=begin_date_sv, width=10)
    end_date_entry = ttk.Entry(mainframe, textvariable=end_date_sv, width=10)
    session_id_label = Label(mainframe, text='oem.sessionid:')
    ltpa_token_label = Label(mainframe, text='LtpaToken:')
    output_path_label = Label(mainframe, text='结果输出完整路径(确保目录已存在):', wraplength=96, justify='right')
    process_label = Label(mainframe, textvariable=process_sv)
    session_id_entry = ttk.Entry(mainframe, textvariable=session_id_sv)
    ltpa_token_text = Text(mainframe, height=6, width=1)
    output_path_entry = ttk.Entry(mainframe, textvariable=output_path_sv)
    #按钮
    button = ttk.Button(mainframe, text="确定", command=execute)
    #布局
    row_at = 0
    readme.grid(row=row_at, column=0, columnspan=4, sticky=(W,N,E))
    row_at += 1
    begin_date_label.grid(row=row_at, column=0, sticky=E)
    begin_date_entry.grid(row=row_at, column=1, columnspan=2, sticky=W)
    end_date_label.grid(row=row_at, column=1, sticky=E)
    end_date_entry.grid(row=row_at, column=2, columnspan=2, sticky=W)

    row_at += 1
    session_id_label.grid(row=row_at, column=0, sticky=E)
    session_id_entry.grid(row=row_at, column=1, columnspan=2, sticky=(W,E))
    row_at += 1
    ltpa_token_label.grid(row=row_at, column=0, sticky=E)
    ltpa_token_text.grid(row=row_at, column=1, columnspan=2, sticky=(W,E))
    row_at += 1
    output_path_label.grid(row=row_at, column=0, sticky=E)
    output_path_entry.grid(row=row_at, column=1, columnspan=2, sticky=(W,E))
    row_at += 1
    # 设置下载进度条
    Label(mainframe, text='解析进度:').grid(row=row_at, column=0, sticky=E)
    canvas = Canvas(mainframe, width=CANVAS_LENGTH, height=22, bg="white")
    canvas.grid(row=row_at, column=1, columnspan=2, sticky=(W,E))
    row_at += 1
    process_label.grid(row=row_at, column=1, columnspan=2, sticky=(W,E))
    row_at += 1
    button.grid(row=row_at, column=1, columnspan=2)
    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)

    # 初始化
    enddate = datetime.datetime.now()
    bgndate = enddate.replace(day=1)
    begin_date_sv.set(bgndate.strftime("%Y%m%d"))
    end_date_sv.set(enddate.strftime("%Y%m%d"))


# 恢复进度条
def reset_progress():
    global canvas
    fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="white")
    canvas.coords(fill_line, (0, 0, CANVAS_LENGTH, 60))


# 刷新进度条
def refresh_progress(cnt, total, title):
    global canvas
    global process_sv
    # 填充进度条
    fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="green")
    n = cnt / total * CANVAS_LENGTH
    canvas.coords(fill_line, (0, 0, n, 60))
    process_sv.set(title)
    mainframe.update()
    #time.sleep(0.02)


# 主UI
def ui_frame():
    win = Tk()
    win.title('产品组OA合同流程跟踪记录抓取小工具')
    win.geometry("800x400+300+100")
    win.resizable(0, 0) # 窗口大小固定
    draw_menu(win)
    draw_frame(win)
    win.mainloop()


# 主程序调用
if __name__ == '__main__':
    ui_frame()
