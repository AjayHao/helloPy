#!/usr/bin/python3

import pymysql


def fetch_string():
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "root", "springlab")

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    # 使用 execute()  方法执行 SQL 查询
    cursor.execute("SELECT VERSION()")

    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()

    print ("Database version : %s " % data)

    # 关闭数据库连接
    db.close()


def create_table():
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "root", "springlab")

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    # 使用 execute() 方法执行 SQL，如果表存在则删除
    cursor.execute("DROP TABLE IF EXISTS EMPLOYEE")

    # 使用预处理语句创建表
    sql = """CREATE TABLE EMPLOYEE (
             FIRST_NAME  CHAR(20) NOT NULL,
             LAST_NAME  CHAR(20),
             AGE INT,  
             SEX CHAR(1),
             INCOME FLOAT )"""

    cursor.execute(sql)

    # 关闭数据库连接
    db.close()


def insert_data():

    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "root", "springlab")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 插入语句
    sql = "INSERT INTO EMPLOYEE(FIRST_NAME, \
           LAST_NAME, AGE, SEX, INCOME) \
           VALUES ('%s', '%s',  %s,  '%s',  %s)" % \
          ('Mac', 'Mohan', 20, 'M', 2000)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # 如果发生错误则回滚
        db.rollback()

    # 关闭数据库连接
    db.close()


def queryall():
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "root", "springlab")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT * FROM EMPLOYEE \
           WHERE INCOME > %s" % (1000)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            fname = row[0]
            lname = row[1]
            age = row[2]
            sex = row[3]
            income = row[4]
            # 打印结果
            print ("fname=%s,lname=%s,age=%s,sex=%s,income=%s" % \
                   (fname, lname, age, sex, income ))
    except:
        print ("Error: unable to fetch data")

    # 关闭数据库连接
    db.close()


def update_data():
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "root", "springlab")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 更新语句
    sql = "UPDATE EMPLOYEE SET AGE = AGE + 1 WHERE SEX = '%c'" % ('M')

    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()

    # 关闭数据库连接
    db.close()


class DB:
    def __init__(self, host='localhost', port=3306, db='', user='root', passwd='root', charset='utf8'):
        # 建立连接
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset=charset)
        # 创建游标，操作设置为字典类型
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __enter__(self):
        # 返回游标
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 提交数据库并执行
        self.conn.commit()
        # 关闭游标
        self.cur.close()
        # 关闭数据库连接
        self.conn.close()


def with_sql():
    with DB(host='localhost',user='root',passwd='root',db='springlab') as db:
        db.execute('select * from employee')
    print(db)
    for i in db:
        print(i)
        print(i['FIRST_NAME'])


# 主程序调用
if __name__ == '__main__':
    fetch_string()
    create_table()
    insert_data()
    queryall()
    update_data()
    with_sql()