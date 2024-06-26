from typing import Optional
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    arkgacha_max: int = 300
    arkgacha_proxy: Optional[str] = None
    arkgacha_pool_file: str = ""
    arkgacha_pure_text: bool = False
    arkgacha_auto_update: bool = True
    arkgacha_reply_sender: bool = False
