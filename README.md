# Executive Peer Evaluation System

Система анонимной перекрёстной оценки топ-менеджеров (Head A/B/C) с голосовым вводом.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/rdunaev-dev/executive-peer-evaluation)

## Возможности

- **4 фактора оценки** — Delivery, Ownership, Cross-functional Impact, People & System Leadership
- **Шкала 1-3** с расчётом PersonScore (4-12) и грейда Head A / B / C
- **Анонимная оценка** — руководители оценивают друг друга по уникальным ссылкам
- **Голосовой ввод** — наговаривайте обоснования вместо печати (Web Speech API)
- **Автозаполнение** — при первом запуске автоматически создаются менеджеры и период
- **Агрегированные отчёты** — средние баллы, грейды, все комментарии

## Деплой на Render.com (один клик)

Нажмите кнопку **Deploy to Render** выше, войдите через GitHub, и приложение задеплоится автоматически.

## Локальный запуск

```bash
pip install -r requirements.txt
python app.py
```

Откройте http://localhost:5000

## Админ-панель

Пароль: `admin2026` (можно изменить через переменную окружения `ADMIN_PASSWORD`)

## Технологии

- Python / Flask / Gunicorn
- SQLite (локально) / PostgreSQL (продакшен через DATABASE_URL)
- Tailwind CSS
- Web Speech API (голосовой ввод)
