import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# 创建数据库引擎
engine = create_engine('sqlite:///bbs_data.db', echo=True)
# 创建基类
Base = declarative_base()
quake_new = "{quake_new_url}"

# 定义数据模型
class BBSInfo(Base):
    __tablename__ = 'bbs_info'


    id = Column(Integer, primary_key=True)
    # 增加 uid 字段
    uid = Column(Integer, nullable=False)
    # 增加 资源来源 字段
    source = Column(String, nullable=False)
    # 标题
    title = Column(String, nullable=False)
    # 节点
    node = Column(String, nullable=False)
    # 标签
    tags = Column(String, nullable=True)
    # 内容
    body = Column(Text, nullable=False)
    # 内容编号
    code = Column(String, nullable=True)
    # 采集链接
    thread_link = Column(String, nullable=True)
    # 提取的夸克
    quake_old_href = Column(String, nullable=True)
    # 转换后的链接
    quake_new_href = Column(String, nullable=True)
    # 增加 状态 字段
    status = Column(String, nullable=False, default="正常")
    # 使用 default 参数设置默认值
    create_time = Column(Integer, nullable=True, default=lambda: int(datetime.datetime.now().timestamp()))
    update_time = Column(Integer, nullable=True, default=lambda: int(datetime.datetime.now().timestamp()))

    def __str__(self):
        return f"标题: {self.title}, 链接: {self.thread_link}, 创建时间: {self.create_time}"

    @classmethod
    def add(cls, session, title, body, thread_link, quake_old_href, quake_new_href, code):
        new_info = cls(
            title=title,
            body=body,
            thread_link=thread_link,
            quake_old_href=quake_old_href,
            quake_new_href=quake_new_href,
            code=code,
            create_time=int(datetime.datetime.now().timestamp()),
            update_time=int(datetime.datetime.now().timestamp())
        )
        session.add(new_info)
        session.commit()

    @classmethod
    def batch_add(cls, infos):
        with Session() as session:
            for info in infos:
                # 根据 thread_link 查找记录
                existing_record = session.query(cls).filter_by(thread_link=info.thread_link).first()
                print(existing_record)
                if existing_record:
                    print("记录已存在>>>", info.title)
                    if existing_record.title != info.title:
                        existing_record.title = info.title
                        existing_record.update_time = int(datetime.datetime.now().timestamp())
                        session.add(existing_record)
                else:
                    print("新增记录>>>", info.title)
                    # 如果记录不存在，添加新记录
                    session.add(info)
            # 提交会话
            session.commit()
        return True

    @classmethod
    def paginate(cls, page=1, per_page=20):
        with Session() as session:
            offset = (page - 1) * per_page
            return session.query(cls).order_by(desc(cls.create_time)).offset(offset).limit(per_page).all()

    @classmethod
    def get_total(cls):
        with Session() as session:
            return session.query(cls).count()

    @classmethod
    def get_byid(cls, id):
        with Session() as session:
            return session.query(cls).filter_by(id=id).one()

    # 替换内容中的网盘地址
    def replace_content(self):
        print("替换内容中的网盘地址")
        if quake_new in self.body:
            self.body = self.body.replace(quake_new, "[ttreply]"+self.quake_new_href+"[/ttreply]")
            self.update_time = int(datetime.datetime.now().timestamp())
            with Session() as session:
                session.query(BBSInfo).filter_by(id=self.id).update({
                    'body': self.body,
                    'quake_new_href': self.quake_new_href,
                    'update_time': self.update_time
                })
                session.commit()


# 创建表
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)
