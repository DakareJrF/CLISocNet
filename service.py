from datetime import datetime
from typing import List, Optional

from db import pg_conn
from models import Message, User


def add_user(username: str, full_name: str, pwd: str) -> int:
    """Create a new user and return the assigned user_id."""
    with pg_conn() as conn:
        cur = conn.execute(
            "INSERT INTO social.users(username, full_name, pwd_hash) "
            "VALUES (%s, %s, %s) RETURNING user_id",
            (username, full_name, pwd),  # в реальности — хэш!
        )
        return cur.fetchone()[0]


def find_user(username: str) -> Optional[User]:
    """Return User instance or None if username does not exist."""
    with pg_conn() as conn:
        cur = conn.execute(
            "SELECT user_id, username, full_name, created_at "
            "FROM social.users WHERE username = %s",
            (username,),
        )
        row = cur.fetchone()
        return User(*row) if row else None


def add_friend(user_id: int, friend_name: str) -> None:
    """Add a friendship link between user_id and friend_name."""
    friend = find_user(friend_name)
    if not friend:
        raise ValueError("User not found")
    with pg_conn() as conn:
        conn.execute(
            "CALL social.add_friend(%s, %s)",
            (user_id, friend.user_id),
        )


def remove_friend(user_id: int, friend_name: str) -> None:
    """Remove the friendship link between user_id and friend_name."""
    friend = find_user(friend_name)
    if not friend:
        raise ValueError("User not found")
    with pg_conn() as conn:
        conn.execute(
            "CALL social.remove_friend(%s, %s)",
            (user_id, friend.user_id),
        )


def list_friends(user_id: int) -> List[str]:
    """Return an alphabetically-sorted list of usernames who are friends with user_id."""
    with pg_conn() as conn:
        cur = conn.execute(
            """
            SELECT u.username
            FROM social.friendships f
            JOIN social.users u ON u.user_id = f.friend_id
            WHERE f.user_id = %s AND f.status = 'accepted'
            UNION
            SELECT u.username
            FROM social.friendships f
            JOIN social.users u ON u.user_id = f.user_id
            WHERE f.friend_id = %s AND f.status = 'accepted'
            ORDER BY 1
            """,
            (user_id, user_id),
        )
        return [row[0] for row in cur.fetchall()]


def send_message(sender_id: int, receiver_name: str, text: str) -> int:
    """Send a private message and return the generated message_id."""
    receiver = find_user(receiver_name)
    if not receiver:
        raise ValueError("Receiver not found")
    with pg_conn() as conn:
        cur = conn.execute(
            "SELECT social.send_message(%s, %s, %s)",
            (sender_id, receiver.user_id, text),
        )
        return cur.fetchone()[0]


def get_chat(user_id: int, friend_name: str, limit: int = 50) -> List[Message]:
    """Return up to `limit` most recent messages between user_id and friend_name."""
    friend = find_user(friend_name)
    if not friend:
        raise ValueError("Friend not found")
    with pg_conn() as conn:
        cur = conn.execute(
            """
            SELECT message_id, sender_id, body, sent_at
            FROM social.get_private_chat(%s, %s, %s)
            """,
            (user_id, friend.user_id, limit),
        )
        return [Message(*row) for row in cur.fetchall()]