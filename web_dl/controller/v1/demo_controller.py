# -*- coding: utf-8 -*-
from webob.response import Response
from web_dl.handler import Handler

# 导入:
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()

# 定义User对象:
class User(Base):
     __tablename__ = 'users'

     id = Column(Integer, primary_key=True)
     name = Column(String(255))
     fullname = Column(String(255))
     password = Column(String(255))

     def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
            self.name, self.fullname, self.password)

def init_db(engine):  # 初始化表
     Base.metadata.create_all(engine)

def drop_db(engine):  # 删除表
     Base.metadata.drop_all(engine)

class DemoController(object):

    def index(self, req, name):
        return Response("hello world %s"
                        % name)

    def hello(self, req):

        # 初始化数据库连接:
        engine = create_engine('mysql+mysqlconnector://root:peng1234@localhost:3306/blog?charset=utf8')
        init_db(engine)

        # 创建User对象
        ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')
        ed_user2 = User(name='ed3', fullname='Ed Jones3', password='edspassword3')
        ed_user3 = User(name='ed2', fullname='Ed Jones2', password='edspassword2')

        # 创建DBSession 类型
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
    
        # Adding and Update Objects
        session.add(ed_user)
        session.add(ed_user2)
        session.add(ed_user3)

        session.commit()

        # 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
        # user = session.query(User).filter(User.uid=='1').one()
        our_user = session.query(User).filter_by(name='ed')
        print("our_user  ****************:", our_user.all())

        session.commit()
        drop_db(engine)
        return Response("hello")

    def params_show(self, req):
        params = ' '.join(["%s %s" % (k, v)
                           for k, v in req.params.items()])
        return Response("req: %s" % params)


def create_handler():
    return Handler(DemoController())
