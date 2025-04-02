from sqlalchemy.orm import relationship
from sqlalchemy import Column, Boolean, Integer, String, ForeignKey

from app.core.db import Base


class User(Base):
    yandex_id = Column(Integer)
    login = Column(String(128))
    email = Column(String(128))
    is_superuser = Column(Boolean)
    is_active = Column(Boolean)
    audio_files = relationship(
        'UserAudioFile', back_populates='user', lazy='selectin'
    )


class UserAudioFile(Base):

    name = Column(String(256))
    file_path = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('User', back_populates='audio_files')
