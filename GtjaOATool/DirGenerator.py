import os
import os.path
import re
import shutil

import pandas as pd

DIR_DICT = {'参数管理': ['建账资料', '合同参数', '运营参数', '增值税管理', '转入材料'],
            '场外业务': ['标的确权材料', '标的净值材料', '衍生品', '银行间'],
            '开放业务': ['开放材料', '折算比例'],
            '清盘与销户': ['清盘', '销户'],
            '管理费用': None,
            '对外披露材料': ['估值材料', '财务报表', '信披核对'],
            '其他估值材料': ['估值材料', '托管核对反馈', '业务提醒']
            }
#output_list_path = 'C:/Users/AjayHao/Desktop/20_托管估值（新）'
input_list_path = 'C:/Users/AjayHao/Desktop/newProductData.csv'
output_list_path_wbgz = 'Z:/19_外包估值（新）'
output_list_path_tggz = 'Z:/20_托管估值（新）'
error_file = 'C:/Users/AjayHao/Desktop/error.txt'
del_input_path = 'C:/Users/AjayHao/Desktop/delete_file.csv'
fill_up_path = 'C:/Users/AjayHao/Desktop/fillUp.txt'
dir_sheet_path = 'C:/Users/AjayHao/Desktop/listsheet.txt'
dir_sheet_path2 = 'C:/Users/AjayHao/Desktop/16_清盘产品.txt'
transfer_csv_path = 'C:/Users/AjayHao/Desktop/dir_transfer.csv'


def generate_dir_files():
    df = pd.read_csv(input_list_path, sep=',', usecols=[0, 1, 2, 3], dtype={'productCode': str}, encoding='GBK')
    #manager_group = dict(list(df.groupby('managerName')))
    #for k,v in manager_group:
    #    generate_by_manager_name(k, v)
    for tuple in df.itertuples():
        #print(tuple)
        if getattr(tuple, 'serviceMode') == '单外包':
            generate_tuple(tuple, output_list_path_wbgz)
        elif getattr(tuple, 'serviceMode') == '单托管':
            generate_tuple(tuple, output_list_path_tggz)
        elif getattr(tuple, 'serviceMode') == '托管与外包':
            generate_tuple(tuple, output_list_path_tggz)
            generate_tuple(tuple, output_list_path_wbgz)


def transfer_files():
    df = pd.read_csv(transfer_csv_path, sep=',', usecols=[0, 1, 2, 3,4,5,6], dtype={'prodCode': str,'datePart': str}, encoding='GBK')
    for tuple in df.itertuples():
        #print(tuple)
        transfer_dir(tuple)


def transfer_dir(tuple):
    src_path = getattr(tuple, 'sourceDir')
    target_path = getattr(tuple, 'targetDir')
    date = getattr(tuple, 'datePart')
    if not pd.isnull(getattr(tuple, 'prodName')):
        target_path_final = target_path + '/' + date
        #todo 后续不能删目录
        try:
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            os.makedirs(target_path_final)

            if os.path.isdir(src_path) :
                copyfullpath(src_path, target_path_final)
            else :
                try:
                    shutil.copy(src_path, target_path_final)
                    print('拷贝完成：' + src_path + " -> " + target_path_final)
                except:
                    write_to_file(error_file, '拷贝文件异常:'+ src_path)
        except:
            write_to_file(error_file, '删目录异常:'+ target_path)

def del_dir():
    df = pd.read_csv(del_input_path, sep=',', usecols=[0, 1, 2], dtype={'productCode': str})
    for tuple in df.itertuples():
        manager_name = re.sub(r'\\|/|:|\*|\?|"|<|>|\|', '', getattr(tuple, 'managerName'))
        del_path = f"{output_list_path}/{manager_name}/{getattr(tuple, 'productCode')}_{getattr(tuple, 'productName')}"
        print(del_path)
        try:
            shutil.rmtree(del_path)
        except:
            write_to_file(error_file, del_path)


def generate_tuple(tuple, output_list_path):
    # 正则替换掉异常字符
    manager_name = re.sub(r'\\|/|:|\*|\?|"|<|>|\|', '', getattr(tuple, 'managerName'))
    product_path = f"{output_list_path}/{manager_name}/{getattr(tuple, 'productCode')}_{getattr(tuple, 'productName')}"
    print(product_path)
    generate(product_path)
    common_path = f"{output_list_path}/{manager_name}/公用"
    if not os.path.exists(common_path):
        generate(common_path)


def generate(path):
    try:
        for key, val in DIR_DICT.items():
            if val is None:
                biz_path = f"{path}/{key}"
                print(biz_path)
                os.makedirs(name=biz_path, exist_ok=True)
            else:
                for sub_biz in val:
                    biz_path = f"{path}/{key}/{sub_biz}"
                    print(biz_path)
                    os.makedirs(name=biz_path, exist_ok=True)
    except:
        write_to_file(error_file, path)


#记录错误日志
def write_to_file(file_path, line):
    with open(file_path, 'a') as fi:
        fi.writelines(list(line))
        fi.write('\n')


#补单逻辑
def fillup():
    with open(fill_up_path, 'r') as fo:
        for line in fo.readlines():
            line = line.strip()
            generate(line)


#检索目录
def printDir():
    basedir = 'Z:/10_外包估值/外包估值开放小组/开放材料/TA开放估值依据-2020/'
    dates = os.listdir(basedir)
    for da in dates:
        if os.path.isdir(basedir + '/' + da):
            filenames = os.listdir(basedir + '/' + da)
            for filename in filenames:
                matchobj = re.match( r'【(.*)】.*', filename, re.M|re.I)
                matchname = '无法识别产品名称'
                if matchobj:
                    matchname = matchobj.group(1)
                isdir = '文件'
                if os.path.isdir(basedir + '/' + da):
                    isdir = '目录'
                linelist = [da, filename, matchname, isdir]
                print(linelist)
                write_to_file(dir_sheet_path, ','.join(linelist))


#检索目录
def printDir2():
    basedir = 'Z:/16_清盘产品/'
    products = os.listdir(basedir)
    for p in products:
        if os.path.isdir(basedir + '/' + p):
            matchobj = re.match( r'(\w*-).*', p, re.M|re.I)
            matchcode = '无法识别产品代码'
            if matchobj:
                matchcode = matchobj.group(1)[0:-1]
            linelist = [p, "'"+matchcode]
            print(linelist)
            write_to_file(dir_sheet_path2, ','.join(linelist))


#通过校验MD5 判断B内的文件与A 不同
def get_MD5(file_path):
    files_md5 = os.popen('md5 %s' % file_path).read().strip()
    file_md5 = files_md5.replace('MD5 (%s) = ' % file_path, '')
    return file_md5


def copyfullpath(path, out):
    for files in os.listdir(path):
        name = os.path.join(path, files)
        back_name = os.path.join(out, files)
        if os.path.isfile(name):
            # if os.path.isfile(back_name):
            #     if get_MD5(name) != get_MD5(back_name):
            #         shutil.copy(name,back_name)
            # else:
            #     shutil.copy(name, back_name)
            try:
                shutil.copy(name, back_name)
                print('拷贝完成：' + name + " -> " + back_name)
            except:
                write_to_file(error_file, '拷贝文件异常:'+ name)
        else:
            if not os.path.isdir(back_name):
                try:
                    os.makedirs(back_name)
                except:
                    write_to_file(error_file, '创建目录异常:'+back_name)
            copyfullpath(name, back_name)


#主程序调用
if __name__ == '__main__':
    # 生成目录清单
    generate_dir_files()
    # 删目录
    #del_dir()
    # 补文件
    #fillup()
    # 打印目录
    #printDir()
    #printDir2()
    # 开放材料迁移
    #transfer_files()