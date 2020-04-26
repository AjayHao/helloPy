import pandas as pd
import os
import os.path

DIR_DICT = {'参数管理': ['建账资料', '合同参数', '运营参数', '增值税管理', '转入材料'],
            '场外业务': ['标的确权材料', '标的净值材料', '衍生品', '银行间'],
            '开放业务': ['开放材料', '折算比例'],
            '清盘与销户': ['清盘', '销户'],
            '管理费用': None,
            '对外披露材料': ['估值材料', '财务报表', '信披核对'],
            '其他估值材料': ['估值材料', '托管核对反馈', '业务提醒']
            }
input_list_path = 'C:/Users/AjayHao/Desktop/test.csv'
output_list_path = 'C:/Users/AjayHao/Desktop/外包估值（新）'


def execute():
    # 读取数据
    read_data()


def read_data():
    df = pd.read_csv(input_list_path, sep=',', usecols=[0, 1, 2])
    #manager_group = dict(list(df.groupby('managerName')))
    #for k,v in manager_group:
    #    generate_by_manager_name(k, v)
    for tuple in df.itertuples():
        #print(tuple)
        generate_tuple(tuple)


def generate_tuple(tuple):
    product_path = f"{output_list_path}/{getattr(tuple, 'managerName')}/{getattr(tuple, 'productCode')}{getattr(tuple, 'productName')}"
    print(product_path)
    generate(product_path)
    common_path = f"{output_list_path}/{getattr(tuple, 'managerName')}/公用"
    if not os.path.exists(common_path):
        generate(common_path)


def generate(path):
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


# 主程序调用
if __name__ == '__main__':
    execute()