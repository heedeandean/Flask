# 사용자 정보에 대한 model 모듈.

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from photolog.model import Base

# [DB - sqlite] users 테이블 생성
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(55), unique=False)

    photos = relationship('Photo',
                          backref='users',
                          cascade='all, delete, delete-orphan')

    def __init__(self, name, email, password):
        self.username = name
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r %r>' % (self.username, self.email)
    