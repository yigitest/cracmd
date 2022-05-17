from pydantic import BaseModel, BaseSettings
from typing import List


class Web3Config(BaseSettings):

    RPC_URL: str = ""
    CHAIN_ID: int = 43114

    USER_ADDRESS: str = ""
    USER_PRIVATE_KEY: str = ""

    CONTRACT_ADDRESS: str = "0x82a85407bd612f52577909f4a58bfc6873f14da8"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
