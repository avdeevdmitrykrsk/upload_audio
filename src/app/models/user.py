from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey

from app.core.db import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    login = Column(String())
    audio_files = relationship('AudioFile', back_populates='user')


class UserAudioFile(Base):
    __tablename__ = 'audio_files'

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True)
    name = Column(String(256))
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('User', back_populates='audio_files')
