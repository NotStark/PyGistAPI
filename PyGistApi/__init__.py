import sys
import os
from typing import Optional
from .sync_gist_api import GistClient
from .async_gist_api import AsyncGistClient

assert sys.version_info[0] == 3, "Python version must be 3"


auth_token: str = os.environ.get("AUTH_TOKEN")
auth_token_path: Optional[str] = os.environ.get("AUTH_TOKEN_PATH")


__author__ = "Siddharth Sharma"
__url__ = "https://github.com/NotStark/PyGistApi"
__description__ = "A Python wrapper around the Github's Gist Rest Api"
__license__ = "MIT"
__version__ = "1.0.0"

__all__ = ["GistClient", "AsyncGistClient"]
