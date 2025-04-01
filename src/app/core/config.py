from pydantic import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'Загрузи аудио-файл'
    secret: str = 'SECRET'

    class Config:
        env_file = '.env'


settings = Settings()
