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
    # 表的名字:
    __tablename__ = 'user'

    # 表的结构:
    uid = Column(Integer, primary_key=True)
    uname = Column(String(32))
    upassword = Column(String(32))


class DemoController(object):

    def index(self, req, name):
        return Response("hello world %s"
                        % name)

    def hello(self, req):
        #import pdb; pdb.set_trace()
        # 初始化数据库连接:
        engine = create_engine('mysql+mysqlconnector://root:peng1234@localhost:3306/web_test_1')
        # 创建DBSession类型:
        DBSession = sessionmaker(bind=engine)
        # 创建Session:
        session = DBSession()
        # 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
        user = session.query(User).filter(User.uid=='1').one()
        # 打印类型和对象的name属性:
        print("hhhh-2021-9-21")
        print ('type2:', type(user))
        print ('name2:', user.uname)
        return Response("hello")

    def params_show(self, req):
        params = ' '.join(["%s %s" % (k, v)
                           for k, v in req.params.items()])
        return Response("req: %s" % params)


def create_handler():
    return Handler(DemoController())
