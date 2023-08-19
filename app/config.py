from pydantic_settings import BaseSettings, SettingsConfigDict

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
    # sender_id:str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()