from datetime import datetime
from dataclasses import dataclass

@dataclass
class User:
    user_id: int
    username: str
    full_name: str
    created_at: datetime

@dataclass
class Message:
    message_id: int
    sender_id: int
    body: str
    sent_at: datetime