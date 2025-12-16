socnet_cli/
├─ cli.py          – точка входа (argparse)
├─ db.py           – контекстный менеджер соединения
├─ models.py       – dataclasses User, Message …
├─ service.py      – вся бизнес-логика (добавить друга, написать …)
└─ config.py       – DSN для PostgreSQL
