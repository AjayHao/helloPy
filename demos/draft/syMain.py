from WindPy import w
import numpy as np
import pandas as pd
import re
from scipy.stats import linregress
from scipy.stats import norm
import datetime
import warnings
import sys

warnings.filterwarnings("ignore")

def solvePosition(series):
    series.index = series.index.astype(str)
    position_dict = {}
    for i in set(series.index):
        if type(series[i]) == pd.Series:
            if sum(series[i]) != 0:
                position_dict[i] = sum(series[i])
        else:
            if series[i] != 0:
                position_dict[i] = series[i]


    position_series = pd.Series(position_dict)

    stockRegex = re.compile(r'^[6|3|0]\d{5}')
    etfRegex = re.compile(r'^[5]\d{5}')
    ifRegex = re.compile(r'^I[H|F|C]\d{4}')
    shOptionRegex = re.compile(r'^1\d{7}')
    szOptionRegex = re.compile(r'^9\d{7}')
    cfeOptionRegex = re.compile(r'^IO\d{4}-[C|P]-\d{4}')

    def contractType(s_code):

        if stockRegex.search(s_code) is not None:
            code = stockRegex.search(s_code).group()
            if code[0] == '6':
                return code + '.SH', '股票'
            else:
                return code + '.SZ', '股票'
        elif etfRegex.search(s_code) is not None:
            code = etfRegex.search(s_code).group()
            if code[0] == '5':
                return code + '.SH', 'ETF'
            else:
                return code + '.SZ', 'ETF'
        elif ifRegex.search(s_code) is not None:
            return ifRegex.search(s_code).group() + '.CFE', '期货'
        elif shOptionRegex.search(s_code) is not None:
            return shOptionRegex.search(s_code).group() + '.SH', '期权'
        elif szOptionRegex.search(s_code) is not None:
            return szOptionRegex.search(s_code).group() + '.SZ', '期权'
        elif cfeOptionRegex.search(s_code) is not None:
            return cfeOptionRegex.search(s_code).group() + '.CFE', '期权'
        else:
            return None, None

    index_list = []
    type_list = []
    num_list = []
    for i in position_series.index:
        idx, dtype = contractType(i)
        if idx is not None:
            index_list.append(idx)
            type_list.append(dtype)
            if pd.isnull(position_series[i]) or type(position_series[i]) == str:
                num_list.append(0)
            else:
                num_list.append(position_series[i])
    df = pd.DataFrame([], index=index_list)
    df['数量'] = num_list
    df['类型'] = type_list
    return df.sort_values(by=['类型'])


def classify(df, date):
    long_series = df[df['类型'] == '股票']['数量']
    if len(long_series) == 0:
        long_series = None
    else:
        long_df = pd.DataFrame([], columns=['名称', '数量', '价格', '市值'], index=long_series.index)
        temp_df = w.wss(','.join(long_df.index), "sec_name,close",
                        "tradeDate={};priceAdj=U;cycle=D".format(date)).Data
        long_df['数量'] = long_series
        long_df['名称'] = temp_df[0]
        long_df['价格'] = temp_df[1]

        long_df.dropna(inplace=True, subset=['价格'])
        long_df['市值'] = long_df['数量'] * long_df['价格']
        long_value = sum(long_df['市值'])
        # ???
        short_swap_series = pd.Series({'中证500指数空头互换': -1e-6, '沪深300指数空头互换': -1e-6})
        # short_swap_series = pd.Series({'中证500指数空头互换': -5000, '沪深300指数空头互换': -17000})
        # short_swap_series = None
        if_series = df[df['类型'] == '期货']['数量']

    if long_series is None:
        short_series = None
        if_series = df[df['类型'] == '期货']['数量']

    else:
        # short_series = df[(df['类型'] == '期货') & (df['数量'] < 0)]['数量']
        short_series = df[df['类型'] == '期货']['数量']
        if short_swap_series is not None:
            short_series = short_series.append(short_swap_series)
        short_df = pd.DataFrame([], columns=['数量', '价格', '乘数', '市值', '是否期货', '标的指数', '标的价格', '调整市值'],
                                index=short_series.index)
        short_df['数量'] = list(short_series)
        temp_df = w.wss(','.join(short_df.index), "close,contractmultiplier",
                        "tradeDate={};priceAdj=U;cycle=D".format(date)).Data
        short_df['价格'] = np.array(temp_df[0], dtype=np.float32)
        temp_multiplier = np.array(temp_df[1], dtype=np.float32)
        temp_multiplier[np.isnan(temp_multiplier)] = 1
        short_df['乘数'] = temp_multiplier
        short_df['是否期货'] = temp_multiplier > 1
        for idx in short_df.index:
            if short_df.loc[idx]['是否期货']:
                if 'IH' in idx:
                    short_df.loc[idx, '标的指数'] = '000016.SH'
                elif 'IF' in idx:
                    short_df.loc[idx, '标的指数'] = '000300.SH'
                elif 'IC' in idx:
                    short_df.loc[idx, '标的指数'] = '000905.SH'
            else:
                if idx == '510050.SH' or '上证50' in idx:
                    short_df.loc[idx, '标的指数'] = '000016.SH'
                elif idx == '510300.SH' or idx == '159919.SZ' or '沪深300' in idx:
                    short_df.loc[idx, '标的指数'] = '000300.SH'
                elif idx == '510500.SH' or idx == '510510.SH' or '中证500' in idx:
                    short_df.loc[idx, '标的指数'] = '000905.SH'

        for idx in short_df.index:
            if np.isnan(short_df.loc[idx]['价格']):
                short_df.loc[idx, '价格'] = \
                    w.wss(short_df.loc[idx]['标的指数'], "close",
                          "tradeDate={};priceAdj=U;cycle=D".format(date)).Data[0][0]
                short_df.loc[idx, '标的价格'] = short_df.loc[idx]['价格']
            else:
                short_df.loc[idx, '标的价格'] = \
                    w.wss(short_df.loc[idx]['标的指数'], "close",
                          "tradeDate={};priceAdj=U;cycle=D".format(date)).Data[0][0]
                if idx == '510050.SH' or idx == '510300.SH' or idx == '159919.SZ' or idx == '510500.SH' or idx == '510510.SH':
                    short_df.loc[idx, '标的价格'] = short_df.loc[idx]['价格']
        short_df['市值'] = short_df['数量'] * short_df['价格'] * short_df['乘数']
        short_df['调整市值'] = short_df['数量'] * short_df['标的价格'] * short_df['乘数']
        if len(short_df[short_df['是否期货'] == False]['调整市值']) != 0:
            short_swap_value = sum(short_df[short_df['是否期货'] == False]['调整市值'])
            short_if_value = sum(short_df[short_df['是否期货'] == True]['调整市值'])
            if 0.9 <= abs(short_swap_value) / long_value <= 1.1:
                short_series = short_swap_series
            else:
                short_value_deficit = long_value - abs(short_swap_value)
                ratio = - short_value_deficit / short_if_value
                if_short_series = short_df[short_df['是否期货'] == True]['数量']
                if_short_series = np.round(if_short_series * ratio)
                for i in if_short_series.index:
                    short_series[i] = int(if_short_series[i])
                if_num_list = []
                for i in if_series.index:
                    if i in if_short_series.index:
                        if_num_list.append(if_series[i] - int(if_short_series[i]))
                    else:
                        if_num_list.append(if_series[i])
                if_series = pd.Series(if_num_list, index=if_series.index)
        else:

            short_value = sum(short_df['调整市值'])
            ratio = - long_value / short_value
            if_short_series = np.round(short_df['数量'] * ratio)
            short_series = np.round(if_short_series).astype(int)


            if_num_list = []
            for i in if_series.index:
                if i in if_short_series.index:
                    if_num_list.append(if_series[i] - int(if_short_series[i]))
                else:
                    if_num_list.append(if_series[i])
            if_series = pd.Series(if_num_list, index=if_series.index)

    option_series = df[(df['类型'] == '期权') | (df['类型'] == 'ETF')]['数量'].append(if_series)
    if len(option_series[option_series != 0]) == 0:
        option_series = None
    if long_series is not None:
        long_series = long_series[long_series != 0]
    if short_series is not None:
        short_series = short_series[short_series != 0]
    if option_series is not None:
        option_series = option_series[option_series != 0]
    return long_series, short_series, option_series


class AlphaMarginCalculator(object):
    def __init__(self, date, fund_value, long_series, short_series, min_stocks=50, max_stock_weight=0.06,
                 max_300_weight=0.1, backtest_days=1000):
        self.MinStocks = min_stocks
        self.MaxStockWeight = max_stock_weight
        self.BacktestDays = backtest_days
        self.date = date
        self.fund_value = fund_value
        self.long_df, self.long_value = self.get_long_df(long_series.dropna())
        self.short_df = self.get_short_df(short_series.dropna())
        self.short_value = sum(self.short_df['调整市值'])
        self.short_futures_value = sum(self.short_df['调整市值'][self.short_df['是否期货']])
        self.short_weight_dict = self.get_short_weight()
        self.short_futures_weight_dict = self.get_short_futures_weight()

        self.net_position = self.long_value + self.short_value
        self.stock_nums = len(long_series[long_series != 0])
        self.max_stock_weight = max(self.long_df['权重'])
        self.max_300_weight = self.get_max_300_weight()
        self.max_none300_weight = self.get_max_none300_weight()
        self.diversification_flag = True
        if self.stock_nums < self.MinStocks or (self.max_none300_weight < max_stock_weight and
                                                self.max_300_weight < max_300_weight):
            self.diversification_flag = False
        self.benchmark_series = self.get_benchmark()

        self.margin_df = pd.DataFrame([], columns=['基准金额', '关注线比例', '预警线比例', '平仓线比例', '关注线金额', '预警线金额', '平仓线金额'])
        self.margin_df.loc['方向性敞口'] = self.net_position_margin()
        self.margin_df.loc['Alpha收益'] = self.alpha_margin()
        self.margin_df.loc['基差风险'] = self.futures_margin()
        self.margin_df.loc['基金净值'] = self.fund_margin()

    def get_long_df(self, long_series):
        long_series = long_series[long_series != 0]
        long_df = pd.DataFrame([], columns=['名称', '数量', '价格', '市值', '权重'], index=long_series.index)
        long_df.index = long_df.index.astype(str)
        index_list = []
        for i in long_df.index:
            if i.isnumeric():
                if i[0] == '6' and len(i) == 6:
                    index_list.append(i + '.SH')
                else:
                    if len(i) < 6:
                        i = '0' * (6 - len(i)) + i
                    index_list.append(i + '.SZ')
            else:
                index_list.append(i)
        long_df.index = index_list
        long_series.index = index_list
        long_df['数量'] = long_series
        temp_df = w.wss(','.join(long_df.index), "sec_name,close",
                        "tradeDate={};priceAdj=U;cycle=D".format(self.date)).Data
        long_df['名称'] = temp_df[0]
        long_df['价格'] = temp_df[1]

        long_df.dropna(inplace=True, subset=['价格'])
        long_df['市值'] = long_df['数量'] * long_df['价格']
        total_long_value = sum(long_df['市值'])
        long_df['权重'] = long_df['市值'] / total_long_value
        return long_df, total_long_value

    def get_short_df(self, short_series):
        index_list = list(short_series.index)
        for i in range(len(index_list)):
            if ('IH' in index_list[i] or 'IF' in index_list[i] or 'IC' in index_list[i]) and '.CFE' not in index_list[i]:
                index_list[i] = index_list[i] + '.CFE'
        short_df = pd.DataFrame([], columns=['数量', '价格', '乘数', '市值', '是否期货', '标的指数', '标的价格', '调整市值'], index=index_list)
        short_df['数量'] = list(short_series)
        temp_df = w.wss(','.join(short_df.index), "close,contractmultiplier",
                        "tradeDate={};priceAdj=U;cycle=D".format(self.date)).Data
        short_df['价格'] = np.array(temp_df[0], dtype=np.float32)
        temp_multiplier = np.array(temp_df[1], dtype=np.float32)
        temp_multiplier[np.isnan(temp_multiplier)] = 1
        short_df['乘数'] = temp_multiplier
        short_df['是否期货'] = temp_multiplier > 1
        for idx in short_df.index:
            if short_df.loc[idx]['是否期货']:
                if 'IH' in idx:
                    short_df.loc[idx, '标的指数'] = '000016.SH'
                elif 'IF' in idx:
                    short_df.loc[idx, '标的指数'] = '000300.SH'
                elif 'IC' in idx:
                    short_df.loc[idx, '标的指数'] = '000905.SH'
            else:
                if idx == '510050.SH' or '上证50' in idx:
                    short_df.loc[idx, '标的指数'] = '000016.SH'
                elif idx == '510300.SH' or idx == '159919.SZ' or '沪深300' in idx:
                    short_df.loc[idx, '标的指数'] = '000300.SH'
                elif idx == '510500.SH' or idx == '510510.SH' or '中证500' in idx:
                    short_df.loc[idx, '标的指数'] = '000905.SH'

        for idx in short_df.index:
            if np.isnan(short_df.loc[idx]['价格']):
                short_df.loc[idx, '价格'] = \
                w.wss(short_df.loc[idx]['标的指数'], "close", "tradeDate={};priceAdj=U;cycle=D".format(self.date)).Data[0][0]
                short_df.loc[idx, '标的价格'] = short_df.loc[idx]['价格']
            else:
                short_df.loc[idx, '标的价格'] = \
                w.wss(short_df.loc[idx]['标的指数'], "close", "tradeDate={};priceAdj=U;cycle=D".format(self.date)).Data[0][0]
        short_df['市值'] = short_df['数量'] * short_df['价格'] * short_df['乘数']
        short_df['调整市值'] = short_df['数量'] * short_df['标的价格'] * short_df['乘数']
        return short_df

    def get_short_weight(self):
        short_weight_dict = {}
        for key, df in self.short_df.groupby('标的指数'):
            short_weight_dict[key] = sum(df['调整市值']) / self.short_value
        return short_weight_dict

    def get_short_futures_weight(self):
        short_futures_weight_dict = {}
        for key, df in self.short_df[self.short_df['是否期货']].groupby('标的指数'):
            short_futures_weight_dict[key] = sum(df['调整市值']) / self.short_futures_value
        return short_futures_weight_dict

    def get_benchmark(self):
        benchmark_df = \
            w.wsd(','.join(self.short_weight_dict.keys()), "pct_chg", "ED-{}TD".format(self.BacktestDays), self.date,
                  "",
                  usedf=True)[1]

        benchmark_series = pd.Series([0] * len(benchmark_df), index=benchmark_df.index)
        if len(self.short_weight_dict) == 1:
            benchmark_series = benchmark_df['PCT_CHG']
        else:
            for key, weight in self.short_weight_dict.items():
                benchmark_series = benchmark_series + benchmark_df[key] * weight
        return benchmark_series

    def get_max_300_weight(self):
        df_300 = w.wset("indexconstituent", "date={};windcode=000300.SH".format(self.date), usedf=True)[1]
        hs300_top20_list = list(df_300.sort_values(by='i_weight', ascending=False)[:20]['wind_code'])
        max_weight = 0
        for i in self.long_df.index:
            if i in hs300_top20_list:
                weight = self.long_df.loc[i]['权重']
                if weight > max_weight:
                    max_weight = weight
        return max_weight

    def get_max_none300_weight(self):
        df_300 = w.wset("indexconstituent", "date={};windcode=000300.SH".format(self.date), usedf=True)[1]
        hs300_top20_list = list(df_300.sort_values(by='i_weight', ascending=False)[:20]['wind_code'])
        max_weight = 0
        for i in self.long_df.index:
            if i not in hs300_top20_list:
                weight = self.long_df.loc[i]['权重']
                if weight > max_weight:
                    max_weight = weight
        return max_weight

    def net_position_margin(self):
        net_position_basis = np.abs(self.net_position)
        attention_rate = 0
        margin_call_rate = 0
        close_rate = 0
        if self.net_position >= 0:
            attention_rate = 30
            margin_call_rate = 20
            close_rate = 10
        else:
            _, _, close_rate, margin_call_rate, attention_rate = self.compute_quantile(self.benchmark_series, 99, 'max')
        close_rate /= 100
        margin_call_rate /= 100
        attention_rate /= 100
        attention_level = net_position_basis * attention_rate
        margin_call_level = net_position_basis * margin_call_rate
        close_level = net_position_basis * close_rate
        return [net_position_basis, attention_rate, margin_call_rate, close_rate, attention_level, margin_call_level,
                close_level]

    def alpha_margin(self):
        alpha_basis = min(self.long_value, np.abs(self.short_value))
        net_position_basis = np.abs(self.net_position)
        attention_rate = 0
        margin_call_rate = 0
        close_rate = 0

        start_date = self.benchmark_series.index[0]
        end_date = self.benchmark_series.index[-1]

        if self.diversification_flag:
            alpha_hist = pd.Series([0] * len(self.benchmark_series), index=self.benchmark_series.index)
            partition_list = list(np.arange(0, self.stock_nums, 200))
            partition_list.append(self.stock_nums)
            stock_df = pd.DataFrame()
            for i in range(len(partition_list) - 1):
                command_str = ','.join(self.long_df.index[partition_list[i]:partition_list[i + 1]])
                print("正在获取第{}-{}只股票日收益数据................".format(partition_list[i] + 1, partition_list[i + 1]), end='')
                if i == 0:
                    stock_df = w.wsd(command_str, "pct_chg", start_date, end_date, "", usedf=True)[1]
                else:
                    stock_df = pd.concat(
                        [stock_df, w.wsd(command_str, "pct_chg", start_date, end_date, "", usedf=True)[1]], axis=1)
                print("获取成功！")
            print("正在计算持仓股票Alpha收益................", end='')
            for stock in self.long_df.index:
                weight = self.long_df.loc[stock]['权重']
                alpha_hist = alpha_hist + self.get_alpha_series(stock, stock_df[stock], self.benchmark_series) * weight
            print("计算完毕！")
            _, _, close_rate, margin_call_rate, attention_rate = self.compute_quantile(alpha_hist, 1, 'min')
            close_rate = abs(close_rate) / 100
            margin_call_rate = abs(margin_call_rate) / 100
            attention_rate = abs(attention_rate) / 100

        else:
            _, _, close_plus, margin_call_plus, attention_plus = self.compute_quantile(self.benchmark_series, 99, 'max')
            attention_rate = 0.5 + attention_plus / 100
            margin_call_rate = 0.4 + margin_call_plus / 100
            close_rate = 0.3 + close_plus / 100

        attention_level = alpha_basis * attention_rate
        margin_call_level = alpha_basis * margin_call_rate
        close_level = alpha_basis * close_rate
        return [alpha_basis, attention_rate, margin_call_rate, close_rate, attention_level, margin_call_level,
                close_level]

    def futures_margin(self):
        futures_basis = abs(self.short_futures_value)
        if futures_basis == 0:
            return [0] * 7
        futures_list = []
        weight_list = []
        for key, weight in self.short_futures_weight_dict.items():
            if key == '000016.SH':
                futures_list.append('IH.CFE')
            elif key == '000300.SH':
                futures_list.append('IF.CFE')
            elif key == '000905.SH':
                futures_list.append('IC.CFE')
            weight_list.append(weight)
        basis_change_series = None
        start_date = '20151231'
        end_date = self.date
        for i in range(len(futures_list)):
            temp_df = w.wsd(futures_list[i], "if_basis, close", start_date, end_date, "", usedf=True)[1]
            basis_change = (np.array(temp_df['IF_BASIS'])[1:] - np.array(temp_df['IF_BASIS'])[:-1]) / np.array(
                temp_df['CLOSE'])[:-1]
            if i == 0:
                basis_change_series = basis_change * weight_list[i]
            else:
                basis_change_series = basis_change_series + basis_change * weight_list[i]
        _, _, close_rate, margin_call_rate, attention_rate = self.compute_quantile(basis_change_series, 99, 'max')
        attention_level = futures_basis * attention_rate
        margin_call_level = futures_basis * margin_call_rate
        close_level = futures_basis * close_rate
        return [futures_basis, attention_rate, margin_call_rate, close_rate, attention_level, margin_call_level,
                close_level]

    def fund_margin(self):
        fund_basis = self.fund_value
        attention_level = sum(self.margin_df['关注线金额'])
        margin_call_level = sum(self.margin_df['预警线金额'])
        close_level = sum(self.margin_df['平仓线金额'])

        attention_rate = attention_level / fund_basis
        margin_call_rate = margin_call_level / fund_basis
        close_rate = close_level / fund_basis
        return [fund_basis, attention_rate, margin_call_rate, close_rate, attention_level, margin_call_level,
                close_level]

    @staticmethod
    def compute_quantile(array, quantile, by='min'):
        array1 = np.array(array)
        array2 = ((1 + array1[:-1] / 100) * (1 + array1[1:] / 100) - 1) * 100
        array3 = ((1 + array1[:-2] / 100) * (1 + array1[1:-1] / 100) * (1 + array1[2:] / 100) - 1) * 100
        array4 = ((1 + array1[:-3] / 100) * (1 + array1[1:-2] / 100) * (1 + array1[2:-1] / 100) * (
                1 + array1[3:] / 100) - 1) * 100
        array5 = ((1 + array1[:-4] / 100) * (1 + array1[1:-3] / 100) * (1 + array1[2:-2] / 100) * (
                1 + array1[3:-1] / 100) * (1 + array1[4:] / 100) - 1) * 100
        if by == 'min':
            array2 = np.min([array1[1:], array2], axis=0)
            array3 = np.min([array1[2:], array2[1:], array3], axis=0)
            array4 = np.min([array1[3:], array2[2:], array3[1:], array4], axis=0)
            array5 = np.min([array1[4:], array2[3:], array3[2:], array4[1:], array5], axis=0)
        elif by == 'max':
            array2 = np.max([array1[1:], array2], axis=0)
            array3 = np.max([array1[2:], array2[1:], array3], axis=0)
            array4 = np.max([array1[3:], array2[2:], array3[1:], array4], axis=0)
            array5 = np.max([array1[4:], array2[3:], array3[2:], array4[1:], array5], axis=0)
        else:
            raise Exception("参数错误！by只能传递'min'或'max'!")
        matrix = np.array([array1[4:], array2[3:], array3[2:], array4[1:], array5])
        quantile_array = np.percentile(matrix, quantile, axis=1)
        return quantile_array[0], quantile_array[1], quantile_array[2], quantile_array[3], quantile_array[4]

    @staticmethod
    def get_alpha_series(stock, stock_series, index_series, min_window=125, chg_limit=20):
        stock_len = len(stock_series.dropna())
        if stock_len < min_window:
            return pd.Series([0] * len(stock_series), index=stock_series.index)
        else:
            stock_series.fillna(0, inplace=True)
            beta, _, _, _, _ = linregress(index_series[-stock_len:], stock_series[-stock_len:])
            alpha_series = (stock_series - beta * index_series).fillna(0)
            alpha_series[alpha_series > chg_limit] = 0
        return alpha_series


class OptionMarginCalculator(object):
    def __init__(self, date, fund_value, position_series, rf=0.022, base_margin=0.1):
        self.r = rf
        self.date = self.get_date(date)
        self.fund_value = fund_value
        self.if_df = self.get_if_df()
        self.df = self.get_df(position_series)
        self.Delta = sum(self.df['Delta金额'])
        self.Gamma = sum(self.df['Gamma金额']) / 100
        self.Vega = sum(self.df['Vega金额']) / 100
        self.liquidity_df = self.get_liquidity_df()
        print("开始期权策略压力测试................", end='')
        self.stress_test_margin = self.stress_test(printout=False)
        print("期权策略压力测试完成！")
        if len(self.liquidity_df) == 0:
            self.liquidity_margin = 0
        else:
            self.liquidity_margin = sum(self.liquidity_df['流动性保证金']) / self.fund_value
        self.margin = self.stress_test_margin + self.liquidity_margin + base_margin


    @staticmethod
    def process_position(position_series, date):
        cmd_str = ','.join(position_series.index.astype(str))

        temp_df = w.wss(cmd_str, "contractmultiplier,exe_price", "tradeDate={}".format(date), usedf=True)[1]
        info_df = pd.DataFrame([], index=temp_df.index, columns=['数量', '类型'])
        info_df['数量'] = position_series
        type_list = []

        for i in info_df.index:
            if pd.notnull(temp_df.loc[i]['EXE_PRICE']):
                type_list.append('期权')
            elif pd.notnull(temp_df.loc[i]['CONTRACTMULTIPLIER']):
                type_list.append('期货')
            else:
                type_list.append('股票')
        info_df['类型'] = type_list
        return info_df

    @staticmethod
    def BS_price(S, K, r, T, v, option_type):
        d1 = (np.log(S / K) + T * (r + 0.5 * v ** 2)) / (v * np.sqrt(T))
        d2 = d1 - v * np.sqrt(T)
        if option_type == 'Call' or option_type == 'C':
            return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    def get_if_df(self):
        today = datetime.date(int(self.date[:4]), int(self.date[4:6]), int(self.date[-2:]))
        year = today.year
        month = today.month

        contract_list = [(year, month)]
        for i in range(12):
            month += 1
            if month > 12:
                month = month % 12
                year += 1
            contract_list.append((year, month))
        str_list = []
        for i in contract_list:
            if i[1] < 10:
                str_list.append(str(i[0])[-2:] + '0' + str(i[1]))
            else:
                str_list.append(str(i[0])[-2:] + str(i[1]))

        code_list = list(map(lambda x: 'IH' + x + '.CFE', str_list)) + list(map(lambda x: 'IF' + x + '.CFE', str_list))

        temp_df = \
        w.wss(','.join(code_list), "close,if_basis,lasttrade_date", "tradeDate={};priceAdj=U;cycle=D".format(self.date),
              usedf=True)[1]
        if_df = pd.DataFrame([], columns=['价格', '基差', '到期日', '剩余自然日'], index=temp_df.index)
        if_df['价格'] = temp_df['CLOSE']
        if_df['基差'] = temp_df['IF_BASIS']

        for i in temp_df.index:
            timestamp = temp_df.loc[i]['LASTTRADE_DATE']
            if_df.loc[i, '到期日'] = datetime.date(timestamp.year, timestamp.month, timestamp.day)
            if_df.loc[i, '剩余自然日'] = (if_df.loc[i, '到期日'] - today).days
        if_df.dropna(inplace=True)
        if_df['标的价格'] = if_df['价格'] - if_df['基差']
        return if_df

    def S_implied(self, dtype, S, T, us_code):
        if dtype == '期货' or dtype == '股票':
            return S
        else:

            T1 = self.if_df['剩余自然日'][0]
            T2 = self.if_df['剩余自然日'][1]
            T3 = self.if_df['剩余自然日'][2]
            T4 = self.if_df['剩余自然日'][3]
            if_df = None
            if us_code == '510050.SH':
                if_df = self.if_df.iloc[:4]
            else:
                if_df = self.if_df.iloc[4:]
            S_index = if_df['标的价格'][0]
            if T <= T1:
                return S * (1 + if_df.iloc[0]['基差'] / S_index * T / T1)
            elif T >= T4:
                return S * (1 + if_df.iloc[3]['基差'] / S_index * T / T4)
            else:
                if T1 < T <= T2:
                    return S * (if_df.iloc[0]['价格'] + (if_df.iloc[1]['价格'] - if_df.iloc[0]['价格']) * (T - T1) / (
                                T2 - T1)) / S_index
                elif T2 < T <= T3:
                    return S * (if_df.iloc[1]['价格'] + (if_df.iloc[2]['价格'] - if_df.iloc[1]['价格']) * (T - T2) / (
                                T3 - T2)) / S_index
                else:

                    return S * (if_df.iloc[2]['价格'] + (if_df.iloc[3]['价格'] - if_df.iloc[2]['价格']) * (T - T3) / (
                                T4 - T3)) / S_index

    def iv(self, S, K, r, T, price, option_type, epsilon=1e-7, max_iteration=1000):
        x_lower = 0.001
        x_upper = 500.01
        x_mid = (x_lower + x_upper) / 2
        f_lower = self.BS_price(S, K, r, T, x_lower, option_type)
        if f_lower > price:
            return x_lower
        f_upper = self.BS_price(S, K, r, T, x_upper, option_type)
        f_mid = self.BS_price(S, K, r, T, x_mid, option_type)
        count = 0
        while abs(f_mid - price) > epsilon:
            if (f_mid - price) * (f_lower - price) < 0:
                x_upper = x_mid
            else:
                x_lower = x_mid
            f_lower = self.BS_price(S, K, r, T, x_lower, option_type)
            f_upper = self.BS_price(S, K, r, T, x_upper, option_type)
            x_mid = (x_lower + x_upper) / 2
            f_mid = self.BS_price(S, K, r, T, x_mid, option_type)
            count += 1
            if count > max_iteration:
                break
        return x_mid

    @staticmethod
    def delta(S, K, r, T, v, option_type):
        d1 = (np.log(S / K) + T * (r + 0.5 * v ** 2)) / (v * np.sqrt(T))
        if option_type == 'Call' or option_type == 'C':
            return norm.cdf(d1)
        else:
            return norm.cdf(d1) - 1

    def get_date(self, date):
        if type(date) == datetime.date or type(date) == datetime.datetime:
            return date.strftime('%Y%m%d')
        else:
            return str(date)

    @staticmethod
    def gamma(S, K, r, T, v):
        d1 = (np.log(S / K) + T * (r + 0.5 * v ** 2)) / (v * np.sqrt(T))
        return 1 / np.sqrt(2 * np.pi) * np.exp(-d1 * d1 / 2) / (S * v * np.sqrt(T))

    @staticmethod
    def vega(S, K, r, T, v):
        d1 = (np.log(S / K) + T * (r + 0.5 * v ** 2)) / (v * np.sqrt(T))
        return S / np.sqrt(2 * np.pi) * np.exp(-d1 * d1 / 2) * np.sqrt(T)

    def get_df(self, position_series):
        col_list = ['数量', '类型', '行权价', '行权方式', '剩余到期日', '价格', '市值', '标的', '标的价格', '标的隐含价格', '合约乘数',
                    '名义本金', 'Delta', '隐含波动率', 'Delta金额', 'Gamma', 'Gamma金额', 'Vega', 'Vega金额']
        df = pd.DataFrame([], columns=col_list, index=position_series.index.astype(str))


        df['类型'] = self.process_position(position_series, self.date)['类型']
        df['数量'] = position_series
        cmd_str = ','.join(df.index)
        temp_df = w.wss(cmd_str, "close,exe_price,exe_mode,ptmday,underlyingwindcode,contractmultiplier",
                        "tradeDate={};priceAdj=U;cycle=D;CalculationTime=60;AnnualCoefficient=252".format(self.date),
                        usedf=True)[1]
        df['行权价'] = temp_df['EXE_PRICE']
        df['行权方式'] = temp_df['EXE_MODE']
        for i in df.index:
            if df.loc[i]['行权方式'] == '认购':
                df.loc[i, '行权方式'] = 'C'
            elif df.loc[i]['行权方式'] == '认沽':
                df.loc[i, '行权方式'] = 'P'
            else:
                df.loc[i, '行权方式'] = 'N'
        #         df['价格'] = temp_df['CLOSE']
        df['价格'] = temp_df['CLOSE']
        df['剩余到期日'] = temp_df['PTMDAY']
        df['合约乘数'] = temp_df['CONTRACTMULTIPLIER']
        for i in df.index:
            if pd.isnull(df.loc[i]['合约乘数']):
                df.loc[i, '合约乘数'] = 1
        df['市值'] = df['数量'] * df['价格'] * df['合约乘数']
        df['标的'] = temp_df['UNDERLYINGWINDCODE']
        for i in df.index:
            if pd.isnull(df.loc[i]['标的']):
                df.loc[i, '标的'] = i

        us_key = list(set(df['标的']))
        us_val = w.wss(','.join(us_key), "close", "tradeDate={};priceAdj=U;cycle=D".format(self.date)).Data[0]
        us_dict = dict(zip(us_key, us_val))
        us_price_list = []
        for i in df.index:
            us_price_list.append(us_dict[df.loc[i]['标的']])

        df['标的价格'] = us_price_list
        for i in df.index:
            df.loc[i, '标的隐含价格'] = self.S_implied(df.loc[i]['类型'], df.loc[i]['标的价格'], df.loc[i]['剩余到期日'],
                                                 df.loc[i]['标的'])

        for i in df.index:
            if pd.isnull(df.loc[i]['Delta']):
                df.loc[i, 'Delta'] = 1
        df['名义本金'] = df['数量'] * df['标的价格'] * df['合约乘数']
        for i in df.index:
            temp_series = df.loc[i]
            S = temp_series['标的隐含价格']
            K = temp_series['行权价']
            if pd.notnull(temp_series['剩余到期日']):
                T = temp_series['剩余到期日'] / 365
            else:
                T = 0
            price = temp_series['价格']
            option_type = temp_series['行权方式']
            if df.loc[i, '类型'] == '期权':
                v = self.iv(S, K, self.r, T, price, option_type)
                df.loc[i, '隐含波动率'] = v
                df.loc[i, 'Delta'] = self.delta(S, K, self.r, T, v, option_type)
                df.loc[i, 'Gamma'] = self.gamma(S, K, self.r, T, v)
                df.loc[i, 'Vega'] = self.vega(S, K, self.r, T, v)
            else:
                df.loc[i, '隐含波动率'] = 0
                df.loc[i, 'Delta'] = 1
                df.loc[i, 'Gamma'] = 0
                df.loc[i, 'Vega'] = 0

        df['Delta金额'] = df['数量'] * df['标的隐含价格'] * df['合约乘数'] * df['Delta']
        df['Gamma金额'] = df['数量'] * df['Gamma'] * df['标的隐含价格'] ** 2 * df['合约乘数']
        #         df['Vega金额'] = df['数量'] * df['标的隐含价格'] * df['合约乘数'] * df['Vega']
        df['Vega金额'] = df['数量'] * df['合约乘数'] * df['Vega']
        return df

    def stress_test(self, S_lower=-5, S_upper=5, v_lower=-5, v_upper=5, printout=False):
        dS_list = np.arange(S_lower, S_upper + 1, 1) / 100
        dv_list = np.arange(v_lower, v_upper + 1, 1) / 100
        mkt_value = np.sum(self.df['市值'])
        val_list = []
        for dS in dS_list:
            for dv in dv_list:
                st_val = []
                df = self.df.loc[:, ['行权方式', '价格', '标的价格', '标的隐含价格', '行权价', '剩余到期日', '隐含波动率', '市值']]
                for i in df.index:
                    option_type = df.loc[i]['行权方式']
                    v = df.loc[i]['隐含波动率']
                    if v <= 1e-3:
                        if option_type == 'P':
                            st_val.append(df.loc[i]['价格'] - df.loc[i]['标的隐含价格'] * dS)
                        else:
                            st_val.append(df.loc[i]['价格'] + df.loc[i]['标的隐含价格'] * dS)
                    else:
                        v = v + dv
                        S = df.loc[i]['标的隐含价格'] * (1 + dS)
                        K = df.loc[i]['行权价']
                        T = df.loc[i]['剩余到期日'] / 365
                        st_val.append(self.BS_price(S, K, self.r, T, v, option_type))
                df['压力测试价格'] = st_val
                df['压力测试市值'] = df['压力测试价格'] / df['价格'] * df['市值']
                val_list.append(np.sum(df['压力测试市值']) - np.sum(self.df['市值']))
                if printout:
                    print("dS={}, dVol={}, {:.2f}, {:.4f}%".format(dS, dv, val_list[-1], val_list[-1]/self.fund_value*100))
        return np.abs(np.min(val_list) / self.fund_value)

    def get_liquidity_df(self):
        df = self.df[self.df['类型'] == '期权'][['市值', '剩余到期日', '标的价格', '行权价']]
        for i in df.index:
            df.loc[i, '虚实值程度'] = abs(df.loc[i]['标的价格'] / df.loc[i]['行权价'] - 1)
            day_to_maturity = df.loc[i]['剩余到期日']
            if day_to_maturity <= 60:
                df.loc[i, '远月流动性系数'] = 0
            elif day_to_maturity <= 180:
                df.loc[i, '远月流动性系数'] = 0.02
            elif day_to_maturity <= 270:
                df.loc[i, '远月流动性系数'] = 0.03
            else:
                df.loc[i, '远月流动性系数'] = 0.04
            moneyness = df.loc[i]['虚实值程度']
            if moneyness <= 0.05:
                df.loc[i, '虚实值流动性系数'] = 0
            elif moneyness <= 0.1:
                df.loc[i, '虚实值流动性系数'] = 0.03
            elif moneyness <= 0.15:
                df.loc[i, '虚实值流动性系数'] = 0.06
            else:
                df.loc[i, '虚实值流动性系数'] = 0.1
        if len(df) > 0:
            df['流动性保证金'] = np.abs(df['市值']) * (df['远月流动性系数'] + df['虚实值流动性系数'])
        df.fillna(0)
        return df


def save_to_excel(result_df, file_path):
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet('Sheet1')
    cell_format1 = workbook.add_format({'bold': True})
    worksheet.set_column('A:A', 22)
    worksheet.write('A1', '单位净值', cell_format1)
    worksheet.write('A2', '资产净值', cell_format1)

    worksheet.write('A3', '净敞口', cell_format1)
    worksheet.write('A4', '股票持仓数量', cell_format1)
    worksheet.write('A5', '单票集中度', cell_format1)
    worksheet.write('A6', 'Delta敞口', cell_format1)
    worksheet.write('A7', 'Gamma敞口', cell_format1)
    worksheet.write('A8', 'Vega敞口', cell_format1)
    worksheet.write('A9', 'Alpha压力测试', cell_format1)
    worksheet.write('A10', '期权压力测试', cell_format1)
    worksheet.write('A11', '穿透持仓比例', cell_format1)
    worksheet.set_column('B:B', 15)
    # cell_format2 = workbook.add_format({'align': 'center'})
    net_value_format = workbook.add_format({'num_format': '0.0000', 'align': 'right'})
    number_format = workbook.add_format({'num_format': '#,##0', 'align': 'right'})
    ratio_format = workbook.add_format({'num_format': '0.00%', 'align': 'right'})
    worksheet.write('B1', result_df['单位净值'], net_value_format)
    worksheet.write('B2', result_df['资产净值'], number_format)
    worksheet.write('B3', result_df['净敞口'], ratio_format)
    worksheet.write('B4', result_df['股票持仓数量'], number_format)
    worksheet.write('B5', result_df['单票集中度'], ratio_format)
    worksheet.write('B6', result_df['Delta敞口'], ratio_format)
    worksheet.write('B7', result_df['Gamma敞口'], ratio_format)
    worksheet.write('B8', result_df['Vega敞口'], ratio_format)
    worksheet.write('B9', result_df['Alpha压力测试'], ratio_format)
    worksheet.write('B10', result_df['期权压力测试'], ratio_format)
    worksheet.write('B11', result_df['穿透持仓比例'], ratio_format)
    writer.save()


def f_main(date, fund_net_value, fund_value, excel_name):
    df = pd.read_excel(excel_name, index_col=[0])
    result_df = pd.Series([0.0] * 11, index=['单位净值', '资产净值', '净敞口', '股票持仓数量', '单票集中度', 'Delta敞口',
                                             'Gamma敞口', 'Vega敞口', 'Alpha压力测试', '期权压力测试', '穿透持仓比例'])
    result_df['单位净值'] = fund_net_value
    result_df['资产净值'] = fund_value

    if len(df) == 0:
        result_df['净敞口'] = 'N/A'
        result_df['股票持仓数量'] = 'N/A'
        result_df['单票集中度'] = 'N/A'
        result_df['Delta敞口'] = 'N/A'
        result_df['Gamma敞口'] = 'N/A'
        result_df['Vega敞口'] = 'N/A'
        result_df['Alpha压力测试'] = 'N/A'
        result_df['期权压力测试'] = 'N/A'
        result_df['穿透持仓比例'] = 'N/A'
        output_file = '申毅穿透持仓计算结果{}.xlsx'.format(date)
        save_to_excel(result_df, output_file)
        print("已成功输出计算结果至:   {}".format(output_file))
        return

    if '数量' in df.columns:
        position_series = df['数量']
    else:
        position_series = df[df.columns[0]]

    base_margin = 0.1
    df = solvePosition(position_series)
    long_series, short_series, option_series = classify(df, date)
    if long_series is not None and short_series is not None:
        AlphaCalculator = AlphaMarginCalculator(date, fund_value, long_series, short_series)
    else:
        AlphaCalculator = None

    if option_series is not None:
        OptionCalculator = OptionMarginCalculator(date, fund_value, option_series, base_margin=0)
    else:
        OptionCalculator = None


    if AlphaCalculator is not None:
        result_df['净敞口'] = AlphaCalculator.net_position / fund_value
        result_df['股票持仓数量'] = AlphaCalculator.stock_nums
        result_df['单票集中度'] = AlphaCalculator.max_stock_weight
        result_df['Alpha压力测试'] = abs(AlphaCalculator.margin_df['预警线比例'][-1])
    else:
        result_df['净敞口'] = 'N/A'
        result_df['股票持仓数量'] = 'N/A'
        result_df['单票集中度'] = 'N/A'
        result_df['Alpha压力测试'] = 'N/A'

    if OptionCalculator is not None:
        result_df['Delta敞口'] = OptionCalculator.Delta / fund_value
        result_df['Gamma敞口'] = OptionCalculator.Gamma / fund_value
        result_df['Vega敞口'] = OptionCalculator.Vega / fund_value
        result_df['期权压力测试'] = OptionCalculator.margin
    else:
        result_df['Delta敞口'] = 'N/A'
        result_df['Gamma敞口'] = 'N/A'
        result_df['Vega敞口'] = 'N/A'
        result_df['期权压力测试'] = 'N/A'

    if result_df['Alpha压力测试'] == 'N/A' and result_df['期权压力测试'] == 'N/A':
        result_df['穿透持仓比例'] = 'N/A'
    elif result_df['Alpha压力测试'] != 'N/A' and result_df['期权压力测试'] == 'N/A':
        result_df['穿透持仓比例'] = result_df['Alpha压力测试'] + base_margin
    elif result_df['Alpha压力测试'] == 'N/A' and result_df['期权压力测试'] != 'N/A':
        result_df['穿透持仓比例'] = result_df['期权压力测试'] + base_margin
    else:
        result_df['穿透持仓比例'] = result_df['Alpha压力测试'] + result_df['期权压力测试'] + base_margin

    output_file = '申毅穿透持仓计算结果{}.xlsx'.format(date)
    save_to_excel(result_df, output_file)
    print("已成功输出计算结果至:   {}".format(output_file))



if __name__ == '__main__':
    w.start()
    date = str(sys.argv[1])
    fund_net_value = float(sys.argv[2])
    fund_value = float(sys.argv[3])
    excel_name = str(sys.argv[4])

    # date = '20200507'
    # fund_net_value = 1.01
    # fund_value = 200000000
    # excel_name = '持仓示例3.xlsx'

    f_main(date, fund_net_value, fund_value, excel_name)


