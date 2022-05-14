import os


def getenv(key: str, default: str = "") -> str:
    """
    Shorthand to get environment variables
    """
    return os.getenv(key, default)
