import argparse, sys, getpass
from service import (
    add_user, find_user, add_friend, remove_friend,
    list_friends, send_message, get_chat
)
from datetime import datetime

AUTH_USER: str = None  # имя текущего пользователя

def main():
    parser = argparse.ArgumentParser(prog="socnet", description="Социальная сеть в консоли")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # --- auth ---
    sub.add_parser("register", help="Регистрация нового пользователя")
    sub.add_parser("login", help="Войти в систему")

    # --- friends ---
    p_add = sub.add_parser("add-friend", help="Добавить друга")
    p_add.add_argument("username")

    p_rem = sub.add_parser("remove-friend", help="Удалить друга")
    p_rem.add_argument("username")

    sub.add_parser("list-friends", help="Список друзей")

    # --- messages ---
    p_msg = sub.add_parser("send", help="Отправить сообщение")
    p_msg.add_argument("friend")
    p_msg.add_argument("text")

    p_chat = sub.add_parser("chat", help="Показать переписку с другом")
    p_chat.add_argument("friend")
    p_chat.add_argument("-n", "--number", type=int, default=30, help="Сколько последних сообщений")

    args = parser.parse_args()

    # регистрация
    if args.cmd == "register":
        username = input("New username: ").strip()
        if find_user(username):
            sys.exit("User already exists")
        full = input("Full name: ").strip() or username
        pwd  = getpass.getpass("Password: ")
        uid = add_user(username, full, pwd)
        print(f"User {username} registered with id={uid}")
        return

    # логин
    if args.cmd == "login":
        global AUTH_USER
        username = input("Username: ").strip()
        u = find_user(username)
        if not u:
            sys.exit("User not found")
        pwd = getpass.getpass("Password: ")
        # тут должна быть проверка хэша, пока заглушка
        AUTH_USER = username
        print(f"Logged in as {username}")
        return

    # требуется авторизация
    if not AUTH_USER:
        sys.exit("Please login first")

    me = find_user(AUTH_USER)
    assert me is not None

    if args.cmd == "add-friend":
        add_friend(me.user_id, args.username)
        print(f"Friend request sent to {args.username}")

    elif args.cmd == "remove-friend":
        remove_friend(me.user_id, args.username)
        print(f"{args.username} removed from friends")

    elif args.cmd == "list-friends":
        friends = list_friends(me.user_id)
        if friends:
            print("Your friends:")
            for f in friends:
                print(" -", f)
        else:
            print("No friends yet")

    elif args.cmd == "send":
        send_message(me.user_id, args.friend, args.text)
        print("Message sent")

    elif args.cmd == "chat":
        msgs = get_chat(me.user_id, args.friend, args.number)
        if not msgs:
            print("No messages yet")
        for m in reversed(msgs):  # старые вверху
            ts = m.sent_at.strftime("%Y-%m-%d %H:%M")
            sender = "You" if m.sender_id == me.user_id else args.friend
            print(f"{ts}  {sender}: {m.body}")

if __name__ == "__main__":
    main()