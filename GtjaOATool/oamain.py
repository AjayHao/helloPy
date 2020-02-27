from urllib.parse import urlencode
from pyquery import PyQuery as pq
from tkinter import ttk
from tkinter import messagebox
from tkinter import *
import time
import requests
import csv

# 外部传入参数
mainframe = None
begin_date_sv = None
end_date_sv = None
session_id_sv = None
file_type_sv = None
need_detail_sv = None
output_path_sv = None
canvas = None
process_sv = None
output_path = ''
ltpa_token_string = ''
file_type = ''
CANVAS_LENGTH = 450
is_detail_output = False
currentPage = 1
pageSize = 1000
oa_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Host': 'oa.gtja.net'
}


# 抓取合同协议列表
def get_contract_list():
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
                "fileclass": file_type,   #OA006-合同协议 OA012-印章申请
                "requester": "1"
            },
            "Type": "OA_TRANS_Q9902",
            "Page": {
                "CurrentPage": currentPage,
                "PageSize": pageSize
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
        # for key, value in response.cookies.items():
        #     print(key + '=' + value)
    return None


# 抓取合同详情
def get_contract_detail(detail_obj):
    ret = {'ngr': '',
           'sjjbr': '',
           'title': detail_obj['TODOTITLE'],
           'qcrfcsj': '',
           'jwzfcsj': ''}
    open_url = detail_obj['TODOURL'].replace("editdocument", "opendocument")
    cookies = {'LtpaToken': ltpa_token_string}
    # 填抓包内容
    # r.cookies.update(c)  # 更新cookies
    response = requests.get(url=open_url, cookies=cookies, headers=oa_headers)
    response.encoding = 'gbk'
    htmlstr = response.text
    # 需要输出详情
    if is_detail_output:
        if file_type == 'OA006':
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

        if ret['ngr'] != '' and ret['sjjbr'] != '':
            break
    return ret


# 抓取跟踪信息
def get_process_track(detail_obj, ret):
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
        if file_type == 'OA006':
            detail_html_prefix = '【合同协议跟踪信息】-'
        else:
            detail_html_prefix = '【印章申请跟踪信息】-'
        write_file(output_path + detail_html_prefix + detail_obj['TODOTITLE'] + ".html", htmlstr)
    # 解析详情html
    htmlobj = pq(htmlstr)
    tds = htmlobj('table.docoumentTable tr td:nth-child(1)').items()
    for td in tds:
        if (td.text() == '起草' or td.html() == '起草') and ret['qcrfcsj'] == '':
            ret['qcrfcsj'] = td.next().next().next().text()

        if td.text() == '公司领导批示' or td.html() == '公司领导批示':
            ret['jwzfcsj'] = td.next().next().next().text()

        if ret['qcrfcsj'] != '' and ret['jwzfcsj'] != '':
            break
    # test
    # write_file('C:\\Users\\AjayHao\\Desktop\\contract\\ret.json', str(ret))
    print(str(ret))
    return ret


# 输出中间结果（调试用）
def write_file(fullpath, text):
    f = open(file=fullpath, mode='w', encoding='gbk')
    f.write(text)
    # 关闭打开的文件
    f.close()


# 导出excel
def export_as_csv(data_list):
    with open(output_path + 'OA流程拉取结果.csv', 'w', newline='') as csvfile:
        fieldnames = ['qcrfcsj', 'title', 'sjjbr', 'ngr', 'jwzfcsj']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'ngr': '拟稿人', 'sjjbr': '实际经办人', 'title': '标题', 'qcrfcsj': '起草人处理发出时间', 'jwzfcsj': '江伟总发出时间'})
        for item in data_list:
            writer.writerow(item)


# 执行爬数主逻辑
def execute():
    global ltpa_token_string
    global output_path
    global is_detail_output
    global file_type
    # 先重置进度条
    reset_progress()

    ltpa_token_string = ltpa_token_text.get(0.0, "end").strip().replace('\n', '').replace('\r', '')
    output_path = output_path_sv.get()
    if not output_path.endswith('/') and not output_path.endswith('\\'):
        output_path = output_path + '/'
    print(need_detail_sv.get())
    if need_detail_sv.get() == 1:
        is_detail_output = True

        # 查询文件类型
    if file_type_sv.get() == 1:
        file_type = 'OA006'
    else:
        file_type = 'OA012'
    list_resp = get_contract_list()
    contract_list = list_resp['Data']
    #it = iter(contract_list)
    # 需要对excel去重
    excel_dict = {}
    idx = 0
    total = len(contract_list)
    while idx < total:
        item = contract_list[idx]
        ret_tuple = get_contract_detail(item)
        get_process_track(item, ret_tuple)
        if ret_tuple['jwzfcsj'] != '':
            excel_dict[ret_tuple['title']] = ret_tuple
        refresh_progress(idx+1, total, ret_tuple['title'])
        idx += 1
    # test
    #write_file(output_path + 'finalData.json', str(excel_list))
    # 输出excel
    export_as_csv(list(excel_dict.values()))
    messagebox.showinfo("执行完毕", "解析完毕，请到下载目录查看结果")


# 版本信息
def show_version_info():
    messagebox.showinfo("版本信息", "Version：     V0.0.1.alpha\nDeveloper： Ajay Hao\n")


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
    global canvas
    global process_sv
    begin_date_sv = StringVar()
    end_date_sv = StringVar()
    session_id_sv = StringVar()
    file_type_sv = IntVar()
    need_detail_sv = IntVar()
    output_path_sv = StringVar()
    process_sv = StringVar()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    mainframe = Frame(root, height=5, width=480) #bg='black'
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    # 组件
    readme = Label(mainframe, bg='white', text='操作说明：参数均为必填项，其中oem.sessionid与LtpaToken通过以下方式获取：使用特定人员账号在Chrome浏览器上登录OA，并点击个人工作台。等待办展现后，按下F12，选Application标签页，点开左侧Storage->Cookies->https://link.gtja.net，找到这两个名称对应的值(Value)拷贝出即可', anchor='center', wraplength=500, justify='left')
    begin_date_label = Label(mainframe, text='开始日期(yyyyMMdd):')
    end_date_label = Label(mainframe, text='结束日期(yyyyMMdd):')
    begin_date_entry = ttk.Entry(mainframe, textvariable=begin_date_sv)
    end_date_entry = ttk.Entry(mainframe, textvariable=end_date_sv)
    session_id_label = Label(mainframe, text='oem.sessionid:')
    ltpa_token_label = Label(mainframe, text='LtpaToken:')
    output_path_label = Label(mainframe, text='文件输出完整路径(确保已存在):', wraplength=96, justify='right')
    process_label = Label(mainframe, textvariable=process_sv)
    session_id_entry = ttk.Entry(mainframe, textvariable=session_id_sv)
    ltpa_token_text = Text(mainframe, height=7, width=1)
    r1 = Radiobutton(mainframe, text="合同协议", value=1, variable=file_type_sv)
    r2 = Radiobutton(mainframe, text="印章申请", value=2, variable=file_type_sv)
    c1 = Checkbutton(mainframe, text="是否打印详单(长耗时)", wraplength=74, justify='right', variable=need_detail_sv)
    output_path_entry = ttk.Entry(mainframe, textvariable=output_path_sv)
    #按钮
    button = ttk.Button(mainframe, text="确定", command=execute)
    #布局
    readme.grid(row=0, columnspan=4, sticky=(W,N,E))
    begin_date_label.grid(row=1, column=0, sticky=E)
    begin_date_entry.grid(row=1, column=1, sticky=(W,E))
    end_date_label.grid(row=1, column=2, sticky=E)
    end_date_entry.grid(row=1, column=3, sticky=(W,E))
    session_id_label.grid(row=2, column=0, sticky=E)
    session_id_entry.grid(row=2, column=1, columnspan=3, sticky=(W,E))
    ltpa_token_label.grid(row=3, column=0, sticky=E)
    ltpa_token_text.grid(row=3, column=1, columnspan=3, sticky=(W,E))
    output_path_label.grid(row=4, column=0, sticky=E)
    output_path_entry.grid(row=4, column=1, columnspan=3, sticky=(W,E))
    c1.grid(row=5, column=0, sticky=E)
    Label(mainframe, text='选择文案类型:').grid(row=5, column=1, sticky=E)
    r1.grid(row=5, column=2, sticky=E)
    r2.grid(row=5, column=3, sticky=W)
    # 设置下载进度条
    Label(mainframe, text='解析进度:').grid(row=6, column=0, sticky=E)
    canvas = Canvas(mainframe, width=CANVAS_LENGTH, height=22, bg="white")
    canvas.grid(row=6, column=1, columnspan=3, sticky=(W,E))
    process_label.grid(row=7, column=0, columnspan=4, sticky=(W,E))
    button.grid(row=8, column=3, sticky=E)
    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)
    # 初始化
    file_type_sv.set(1)

    #临时
    begin_date_sv.set('20200101')
    end_date_sv.set('20200131')


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
    win.geometry("620x500+300+100")
    win.resizable(0, 0) # 窗口大小固定
    draw_menu(win)
    draw_frame(win)
    win.mainloop()


# 主程序调用
if __name__ == '__main__':
    ui_frame()

