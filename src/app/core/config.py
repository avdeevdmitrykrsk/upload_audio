import os

from pydantic import BaseSettings


class Settings(BaseSettings):

    # postgres
    database_url: str = os.getenv('DATABASE_URL')
    posgres_user: str = os.getenv('POSTGRES_USER')
    postgres_password: str = os.getenv('POSTGRES_PASSWORD')
    postgres_db: str = os.getenv('POSTGRES_DB')
    db_host: int = os.getenv('DB_HOST')
    db_port: int = os.getenv('DB_PORT')

    # auth
    secret_key: str = os.getenv('SECRET_KEY')
    algorithm: str = os.getenv('ALGORITHM')
    exp_refresh_token: int = os.getenv('EXP_REFRESH_TOKEN')
    exp_access_token: int = os.getenv('EXP_ACCESS_TOKEN')
    jwt_access_token_expires: int = 3600
    jwt_refresh_token_expires: int = 86400 * 30

    # Конфигурация Яндекс OAuth
    yandex_auth_url: str = os.getenv('YANDEX_AUTH_URL')
    yandex_token_url: str = os.getenv('YANDEX_TOKEN_URL')
    yandex_user_info_url: str = os.getenv('YANDEX_USER_INFO_URL')

    # Настройки приложения
    client_id: str = os.getenv('CLIENT_ID')
    client_secret: str = os.getenv('CLIENT_SECRET')
    redirect_uri: str = os.getenv('REDIRECT_URI')


settings = Settings()
