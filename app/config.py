from pydantic_settings import BaseSettings, SettingsConfigDict
import os
class Settings(BaseSettings):
    database_username: str
    database_name: str
    database_password: str
    database_port: str
    database_host: str
    secret_key: str
    algorithm: str
    expiry_time_taken: int 
    secret_owner_key: str
    postgresql_url : str

    mysql_url : str
    sender_id:str
    database_username: str = os.environ.get("DATABASE_USERNAME")
    database_name: str = os.environ.get("DATABASE_NAME")
    database_password: str = os.environ.get("DATABASE_PASSWORD")
    database_port: str = os.environ.get("DATABASE_PORT")
    database_host: str = os.environ.get("DATABASE_HOST")
    secret_key: str = os.environ.get("SECRET_KEY")
    algorithm: str = os.environ.get("ALGORITHM")
    expiry_time_taken: int = int(os.environ.get("EXPIRY_TIME_TAKEN", 3600))  # Provide a default value
    secret_owner_key: str = os.environ.get("SECRET_OWNER_KEY")

    # model_config = SettingsConfigDict(env_file=".env")

settings = Settings()


    # database_username: str = os.environ.get("DATABASE_USERNAME")
    # database_name: str = os.environ.get("DATABASE_NAME")
    # database_password: str = os.environ.get("DATABASE_PASSWORD")
    # database_port: str = os.environ.get("DATABASE_PORT")
    # database_host: str = os.environ.get("DATABASE_HOST")
    # secret_key: str = os.environ.get("SECRET_KEY")
    # algorithm: str = os.environ.get("ALGORITHM")
    # expiry_time_taken: int = int(os.environ.get("EXPIRY_TIME_TAKEN", 3600))  # Provide a default value
    # secret_owner_key: str = os.environ.get("SECRET_OWNER_KEY")
