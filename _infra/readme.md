# Design Patterns / Ромашка

### Подготовка окружения

Проект использует [`uv`](https://docs.astral.sh/uv/) для управления
зависимостями и виртуальным окружением (см. `pyproject.toml`,
`.python-version`).

```sh
uv sync
```

Команда создаст `.venv` и установит зависимости согласно `pyproject.toml`.

### Запуск

```sh
uv run main.py
```

### Активация окружения вручную (при необходимости)

```sh
source .venv/bin/activate
```
