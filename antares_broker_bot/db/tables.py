from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    topics = relationship("Topics")


class Topics(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("user.user_id"), nullable=False)
    topic = Column(String(128), nullable=False)
