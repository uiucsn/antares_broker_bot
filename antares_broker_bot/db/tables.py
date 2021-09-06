from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    topics = relationship('Topic', back_populates='user')


class Topic(Base):
    __tablename__ = 'topic'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(User.user_id), nullable=False)
    user = relationship('User', back_populates='topics')
    topic = Column(String, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'topic', name='_user_id_topic_uc'),
    )


class Locus(Base):
    __tablename__ = 'locus'

    id = Column(Integer, primary_key=True)
    locus_id = Column(String(14), nullable=False, index=True)
    topic_id = Column(ForeignKey(Topic.id), nullable=False)

    __table_args__ = (
        UniqueConstraint('locus_id', 'topic_id', name='_locus_id_topic_id_uc'),
    )
