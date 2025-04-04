from app.crud.base import BaseCRUD
from app.models import UserAudioFile


class AudioFileCRUD(BaseCRUD):
    pass


audio_file_crud = AudioFileCRUD(UserAudioFile)
