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
    "V0.1.1 - 20200407: 调整“江伟总”为“公司领导”",
    "V0.1.2 - 20210116: 调整“”"
]

# 外部传入参数
mainframe = None
begin_date_sv = None
leader_date_sv = None
end_date_sv = None
session_id_sv = None
file_type_sv = None
need_detail_sv = None
output_path_sv = None
canvas = None
process_sv = None
button = None
output_path = ''
ltpa_token_string = ''
file_type = ''
is_detail_output = False
unique_set = set()
oa_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Host': 'oa.gtja.net'
}
form_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded'
}

CANVAS_LENGTH = 600
PAGE_SIZE = 10


# 分页取数
def get_contract_list_by_page(page_no):

    url = 'https://link.gtja.net/link/common/oa/ajaxMappingHandler'

    post_param = {
        "data": {
            "Param": {
                "begindate": begin_date_sv.get().strip(),
                "enddate": end_date_sv.get().strip(),
                "fileclass_main": "OA",
                # OA006-合同协议 OA012-印章申请
                # 新OA：EOA005-合同协议 EOA006-印章申请
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
    response = requests.post(url=post_url, data=post_data, headers=form_headers)
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


# 抓取合同详情 - 新
def get_contract_detail_new(detail_obj):
    global unique_set
    ret = {'ngr': '',
           'sjjbr': '',
           'title': detail_obj['TODOTITLE'],
           'qcrfcsj': '',
           'gsldfcsj': '',
           'unique': ''}

    open_url = 'https://link.gtja.net/api/eoagw/eoaflow/flowCommon/flowApi?FLOW_MAIN_Q0001&funcId=FLOW_MAIN_Q0001'

    post_param = {
        "data": {
            "Param": "{\"piid\":\"" + detail_obj['TODONO'] + "\"}",
            "Type": "FLOW_MAIN_Q0001"
        }
    }

    post_data = urlencode(post_param)
    #cookies = {'LtpaToken': ltpa_token_string}
    # 填抓包内容
    # r.cookies.update(c)  # 更新cookies
    response = requests.post(url=open_url, data=post_data, headers=form_headers)
    if response.status_code == 200:
        ret_json = response.json()
        main_data = ret_json['Data']
        tiid = main_data['instFlowTodoPersonList'][-1]['tiid']
        detail_url = 'https://link.gtja.net/api/eoagw/eoaflow/flowCommon/flowApi?FLOW_MAINFORM_Q0001&funcId=FLOW_MAINFORM_Q0001'
        detail_param = {
            "data": {
                "Param": {
                    "piid": detail_obj['TODONO'],
                    "tiid": tiid,
                    "groupFlag": "FLOW_DOC_HTXY"
                },
                "Type": "FLOW_MAINFORM_Q0001"
            }
        }
        detail_data = urlencode(detail_param)
        detail_resp = requests.post(url=detail_url, cookies=cookies, data=detail_data, headers=form_headers)
        if detail_resp.status_code == 200:
            detail_obj = detail_resp.json()
            detail_data = detail_obj['Data'][0]
            ret['ngr'] = detail_data['TXQCR']
            ret['sjjbr'] = detail_data['TXSJJBR']
    return ret


# 抓取合同详情
def get_contract_detail_old(detail_obj):
    global unique_set
    ret = {'ngr': '',
           'sjjbr': '',
           'title': detail_obj['TODOTITLE'],
           'qcrfcsj': '',
           'gsldfcsj': '',
           'unique': ''}
    open_url = detail_obj['TODOURL'].replace("editdocument", "opendocument")
    cookies = {'LtpaToken': ltpa_token_string}
    # 填抓包内容
    # r.cookies.update(c)  # 更新cookies
    response = requests.get(url=open_url, cookies=cookies, headers=oa_headers)
    response.encoding = 'gbk'
    htmlstr = response.text
    # 需要输出详情
    if is_detail_output:
        if file_type == 'EOA005':
            detail_html_prefix = '【合同协议详情】-'
        else:
            detail_html_prefix = '【印章申请详情】-'
        write_file(output_path + detail_html_prefix + detail_obj['TODOTITLE'] +".html", htmlstr)
    # 解析详情html
    htmlobj = pq(htmlstr)
    tds = htmlobj('table.tableForm:first tr td').items()
    for td in tds:
        if td.text() == '拟稿人':
            ret['ngr'] = td.next().text()

        if td.text() == '实际经办人':
            ret['sjjbr'] = td.next().text()

        #唯一性校验
        if td.text() == '文件编号':
            key = td.next().text()
            if key in unique_set:
                ret['unique'] = '0'
            else:
                unique_set.add(key)
                ret['unique'] = '1'

        if ret['ngr'] != '' and ret['sjjbr'] != '' and ret['unique'] != '':
            break
    return ret


# 抓取跟踪信息
def get_process_track_new(detail_obj, contract_obj):
    track_url = 'https://link.gtja.net/api/eoagw/eoaflow/flowCommon/flowApi?FLOW_TRACE_Q0001&funcId=FLOW_TRACE_Q0001'

    track_param = {
        "data": {
            "Param": {
                "piid": detail_obj['TODONO']
            },
            "Type": "FLOW_TRACE_Q0001"
        }
    }
    track_data = urlencode(track_param)
    cookies = {'LtpaToken': ltpa_token_string}
    response = requests.post(url=track_url, cookies=cookies, data=track_data, headers=form_headers)
    if response.status_code == 200:
        ret_json = response.json()
        track_obj_list = ret_json['Data']
        track_obj_list.reverse()
        for track_obj in track_obj_list:
            if track_obj['nodeName'] == '起草' and track_obj['sendTime'] != '':
                st = datetime.datetime.strptime(track_obj['sendTime'],'%Y%m%d%H%M%S')
                contract_obj['qcrfcsj'] = datetime.datetime.strftime(st, '%Y-%m-%d %H:%M:%S')

            if file_type == 'EOA005':
                if track_obj['nodeName'] == '部门负责人签署意见' and track_obj['sendTime'] != '':
                    st = datetime.datetime.strptime(track_obj['sendTime'],'%Y%m%d%H%M%S')
                    contract_obj['gsldfcsj'] = datetime.datetime.strftime(st, '%Y-%m-%d %H:%M:%S')
            else:
                if track_obj['nodeName'] == '公司领导批复' and track_obj['sendTime'] != '':
                    st = datetime.datetime.strptime(track_obj['sendTime'],'%Y%m%d%H%M%S')
                    contract_obj['gsldfcsj'] = datetime.datetime.strftime(st, '%Y-%m-%d %H:%M:%S')

            if contract_obj['qcrfcsj'] != '' and contract_obj['gsldfcsj'] != '':
                break
    # test
    # write_file('C:\\Users\\AjayHao\\Desktop\\contract\\ret.json', str(ret))
    contract_obj['unique'] = '1'
    print(str(contract_obj))
    return contract_obj


# 抓取跟踪信息
def get_process_track_old(detail_obj, contract_obj):
    docid = detail_obj['TODONO']
    url = detail_obj['TODOURL']
    sidx = url.find('nsf')
    track_prefix = url[0:sidx]
    open_url = track_prefix+'nsf/TraceDoc?OpenAgent&Time='+str(time.time)+'&DocID='+docid
    cookies = {'LtpaToken': ltpa_token_string}
    response = requests.get(url=open_url, cookies=cookies, headers=oa_headers)
    response.encoding = 'gbk'
    htmlstr = response.text
    # 需要输出详情
    if is_detail_output:
        if file_type == 'EOA005':
            detail_html_prefix = '【合同协议跟踪信息】-'
        else:
            detail_html_prefix = '【印章申请跟踪信息】-'
        write_file(output_path + detail_html_prefix + detail_obj['TODOTITLE'] + ".html", htmlstr)
    # 解析详情html
    htmlobj = pq(htmlstr)
    tds = htmlobj('table.docoumentTable tr td:nth-child(1)').items()
    for td in tds:
        if (td.text() == '起草' or td.html() == '起草') and contract_obj['qcrfcsj'] == '':
            contract_obj['qcrfcsj'] = td.next().next().next().text()

        if file_type == 'EOA005':
            if td.text() == '部门负责人签署意见' or td.html() == '部门负责人签署意见':
                contract_obj['gsldfcsj'] = td.next().next().next().text()
        else:
            if td.text() == '公司领导批复' or td.html() == '公司领导批复':
                contract_obj['gsldfcsj'] = td.next().next().next().text()

        if contract_obj['qcrfcsj'] != '' and contract_obj['gsldfcsj'] != '':
            break
    # test
    # write_file('C:\\Users\\AjayHao\\Desktop\\contract\\ret.json', str(ret))
    print(str(contract_obj))
    return contract_obj


# 输出中间结果（调试用）
def write_file(path, text):
    decoded_path = path.replace("\t", " ").replace("\x06", "").replace("\x05", "").replace("\x07", "")
    f = open(file=decoded_path, mode='w', encoding='gbk')
    f.write(text)
    # 关闭打开的文件
    f.close()

# 导出excel
def export_as_csv(data_list):
    with open(output_path + 'OA流程拉取结果.csv', 'w', newline='') as csvfile:
        fieldnames = ['qcrfcsj', 'title', 'sjjbr', 'ngr', 'gsldfcsj']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'ngr': '拟稿人', 'sjjbr': '实际经办人', 'title': '标题', 'qcrfcsj': '起草人处理发出时间', 'gsldfcsj': '公司领导发出时间'})
        for item in data_list:
            del item['unique']
            writer.writerow(item)


# 执行爬数主逻辑
def execute():
    global ltpa_token_string
    global output_path
    global is_detail_output
    global file_type

    # 参数校验
    if begin_date_sv.get() == '' or \
            end_date_sv.get() == '' or \
            leader_date_sv.get() == '' or \
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
        if need_detail_sv.get() == 1:
            is_detail_output = True
            # 查询文件类型
        if file_type_sv.get() == 1:
            file_type = 'EOA005'
        else:
            file_type = 'EOA006'
        leader_date_str = leader_date_sv.get()

        # 获得申请列表
        contract_list = get_contract_list()
        #list_resp = get_contract_list()
        #contract_list = list_resp['Data']

        # 需要对excel去重
        #excel_dict = {}
        excel_list = []
        idx = 0
        total = len(contract_list)
        while idx < total:
            item = contract_list[idx]
            if item['TODOURL'] != '' and item['TODOURL'].find('EOA') > 0:
                ret_tuple = get_contract_detail_new(item)
                get_process_track_new(item, ret_tuple)
            else:
                ret_tuple = get_contract_detail_old(item)
                get_process_track_old(item, ret_tuple)

            if ret_tuple['gsldfcsj'] != '' and ret_tuple['gsldfcsj'] != '未结束' and ret_tuple['unique'] == '1':
                #excel_dict[ret_tuple['title']] = ret_tuple
                # 判断公司领导时间是否落在这个区间  "%Y-%m-%d %H:%M:%S"
                t1 = datetime.datetime.strptime(ret_tuple['gsldfcsj'],'%Y-%m-%d %H:%M:%S')
                gsldfcsj = t1.strftime("%Y%m")
                if gsldfcsj == leader_date_str:
                    excel_list.append(ret_tuple)
            refresh_progress(idx+1, total, ret_tuple['title'])
            idx += 1
        # test
        #write_file(output_path + 'finalData.json', str(excel_list))
        # 输出excel
        #excel_list = list(excel_dict.values())
        export_as_csv(excel_list)
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
    global file_type_sv
    global need_detail_sv
    global ltpa_token_text
    global output_path_sv
    global leader_date_sv
    global canvas
    global process_sv
    global button
    begin_date_sv = StringVar()
    end_date_sv = StringVar()
    leader_date_sv = StringVar()
    session_id_sv = StringVar()
    file_type_sv = IntVar()
    need_detail_sv = IntVar()
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
    begin_date_entry = ttk.Entry(mainframe, textvariable=begin_date_sv, width=20)
    end_date_entry = ttk.Entry(mainframe, textvariable=end_date_sv, width=20)
    session_id_label = Label(mainframe, text='oem.sessionid:')
    ltpa_token_label = Label(mainframe, text='LtpaToken:')
    output_path_label = Label(mainframe, text='结果输出完整路径(确保目录已存在):', wraplength=96, justify='right')
    process_label = Label(mainframe, textvariable=process_sv)
    session_id_entry = ttk.Entry(mainframe, textvariable=session_id_sv)
    ltpa_token_text = Text(mainframe, height=5, width=1)
    r1 = Radiobutton(mainframe, text="合同协议", value=1, variable=file_type_sv)
    r2 = Radiobutton(mainframe, text="印章申请", value=2, variable=file_type_sv)
    c1 = Checkbutton(mainframe, text="是否下载详情(将明细文件保存至输出路径)", variable=need_detail_sv)
    output_path_entry = ttk.Entry(mainframe, textvariable=output_path_sv)
    #按钮
    button = ttk.Button(mainframe, text="确定", command=execute)
    #布局
    row_at = 0
    readme.grid(row=row_at, columnspan=6, sticky=(W,N,E))
    row_at += 1
    begin_date_label.grid(row=row_at, column=0, sticky=E)
    begin_date_entry.grid(row=row_at, column=1, sticky=W)
    end_date_label.grid(row=row_at, column=2, sticky=E)
    end_date_entry.grid(row=row_at, column=3, sticky=W)
    Label(mainframe, text='公司领导审批通过所在月(yyyyMM):', wraplength=110, justify='right').grid(row=row_at, column=4, sticky=E)
    ttk.Entry(mainframe, textvariable=leader_date_sv, width=10).grid(row=row_at, column=5, sticky=(W,E))

    row_at += 1
    Label(mainframe, text='选择文案类型:').grid(row=row_at, column=0, sticky=E)
    r1.grid(row=row_at, column=1, sticky=E)
    r2.grid(row=row_at, column=2, sticky=W)
    c1.grid(row=row_at, column=3, columnspan=3, sticky=W)

    row_at += 1
    session_id_label.grid(row=row_at, column=0, sticky=E)
    session_id_entry.grid(row=row_at, column=1, columnspan=5, sticky=(W,E))
    row_at += 1
    ltpa_token_label.grid(row=row_at, column=0, sticky=E)
    ltpa_token_text.grid(row=row_at, column=1, columnspan=5, sticky=(W,E))
    row_at += 1
    output_path_label.grid(row=row_at, column=0, sticky=E)
    output_path_entry.grid(row=row_at, column=1, columnspan=5, sticky=(W,E))
    row_at += 1
    # 设置下载进度条
    Label(mainframe, text='解析进度:').grid(row=row_at, column=0, sticky=E)
    canvas = Canvas(mainframe, width=CANVAS_LENGTH, height=22, bg="white")
    canvas.grid(row=row_at, column=1, columnspan=4, sticky=(W,E))
    row_at += 1
    process_label.grid(row=row_at, column=1, columnspan=4, sticky=(W,E))
    row_at += 1
    button.grid(row=row_at, column=2, columnspan=2)
    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)
    # 初始化
    file_type_sv.set(1)

    enddate = datetime.datetime.now()
    bgndate = enddate.replace(day=1)
    begin_date_sv.set(bgndate.strftime("%Y%m%d"))
    end_date_sv.set(enddate.strftime("%Y%m%d"))
    leader_date_sv.set(bgndate.strftime("%Y%m"))

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
    win.title('产品组OA绩效抓取小工具')
    win.geometry("840x430+300+100")
    win.resizable(0, 0) # 窗口大小固定
    draw_menu(win)
    draw_frame(win)
    win.mainloop()



# 主程序调用
if __name__ == '__main__':
    ui_frame()
    #write_file("C:\\Users\\AjayHao\\Desktop\\contract\\【AA类】 · S22922，宁聚满天星，补充协议（四）.html", "哎哎哎")