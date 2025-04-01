# Standart lib imports
from typing import List, Optional

# Thirdparty imports
from pydantic import BaseModel


class UserAudioFileRead(BaseModel):
    id: int
    name: str
    file_path: str

    class Config:
        orm_mode = True


class UserRead(BaseModel):
    yandex_id: int
    login: str
    email: str
    is_superuser: bool
    is_active: bool
    audio_files: List[UserAudioFileRead] = []

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    pass


class UserUpdate(BaseModel):
    yandex_id: Optional[int]
    login: Optional[str]
    email: Optional[str]
    is_superuser: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
