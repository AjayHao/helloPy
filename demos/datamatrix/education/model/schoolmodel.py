#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' school orm '

__author__ = 'Ajay Hao'

from sqlalchemy import Column, String, CLOB, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()
# 初始化数据库连接:
engine = create_engine('mysql+pymysql://root:root@localhost:3306/test?charset=utf8')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)


class School(Base):
    # 表的名字:
    __tablename__ = 'sh_school'

    # 表的结构:
    id = Column(String(32), primary_key=True)
    data_year = Column(String(8))
    name = Column(String(150))
    area = Column(String(300))
    level = Column(String(30))
    type = Column(String(10))
    address = Column(String(600))
    edu_type = Column(String(30))
    info = Column(CLOB)

    def __repr__(self):
        return "<School(name='%s')>" % self.name
