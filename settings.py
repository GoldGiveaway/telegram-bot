from pydantic import SecretStr
from services.yaml_reader import YAMLSettings, YAMLSettingsConfig


class Settings(YAMLSettings):
    api_token: SecretStr
    mongodb_url: SecretStr

    redis_host: str
    redis_port: int
    redis_db: int

    model_config = YAMLSettingsConfig(env_file_encoding="utf-8", yaml_file=("config.yml",))

