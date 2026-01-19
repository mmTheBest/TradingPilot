from dataclasses import dataclass
from typing import Optional


@dataclass
class ChatEvent:
    platform: str
    user_id: str
    text: str
    action: Optional[str] = None
