"""
Seed data for the Executive Peer Evaluation System.
Auto-populates the database on first startup if empty.
Preserves existing tokens so evaluation links remain stable.
"""

SEED_MANAGERS = [
    ("Антон Андрюшин", "Head of Winscore / Product Lead", "a.andryushin@rantsports.com"),
    ("Алик Паршин", "Head of Project Office (PMO)", "a.parshin@rantsports.com"),
    ("Василий Мехонцев", "Head of Monetisation", "v.mekhontsev@rantsports.com"),
    ("Дмитрий Панфёров", "Head of Engagement", "d.panferov@rantsports.com"),
    ("Евгений Куприянов", "Консультант по организационной зрелости", "e.kupriyanov@rantsports.com"),
    ("Мария Вилистер", "Head of Back Office", "m.vilister@rantsports.com"),
    ("Максим Ракутько", "Head of Analytics", "m.rakutko@rantsports.com"),
    ("Николай Крицюк", "Head of Tech", "n.kritsiuk@rantsports.com"),
    ("Олег Панасюк", "Head of Media / Главный редактор", "o.panasyuk@rantsports.com"),
    ("Павел Сидогов", "Head of SEO", "p.sidogov@rantsports.com"),
    ("Роман Дунаев", "Head of HR", "r.dunaev@rantsports.com"),
]

SEED_PERIOD = {
    "name": "Q3-Q4 2025 (июль — декабрь 2025)",
    "description": "Перекрёстная оценка руководителей за последние 6 месяцев. Шкала 1-3 по 4 факторам: Delivery, Ownership, Cross-functional Impact, People & System Leadership.",
    "start_date": "2025-07-01",
    "end_date": "2025-12-31",
}

SEED_TOKENS = {
    "Антон Андрюшин": "6214a498-a0d4-4798-a46e-8747b0dda3af",
    "Алик Паршин": "8b77c3ed-c9a8-41a8-9373-3abd194ed58a",
    "Василий Мехонцев": "ab03a69b-1bf5-4581-85c5-167486bcaf17",
    "Дмитрий Панфёров": "3238cb85-152c-4d56-a31a-57b645047daa",
    "Евгений Куприянов": "e0b552f5-abc7-41f3-97cd-cd289b86cab6",
    "Мария Вилистер": "b19180cf-a49b-4729-a1f6-659e931c04df",
    "Максим Ракутько": "7b57bfeb-7485-4561-a388-b731e21e0245",
    "Николай Крицюк": "d132a61e-2503-4be8-859f-b69c38b714ee",
    "Олег Панасюк": "ba20b970-e05d-40ee-b554-86b56f18d740",
    "Павел Сидогов": "1a7b7708-8057-4cd3-a09a-152d9d120db9",
    "Роман Дунаев": "58f29530-cd79-4d74-b859-f87c05dbfd05",
}


def auto_seed(get_db_func):
    """Populate the database with seed data if it's empty."""
    conn = get_db_func()
    count = conn.execute("SELECT COUNT(*) as cnt FROM managers").fetchone()

    cnt = count['cnt'] if isinstance(count, dict) else count[0]
    if cnt > 0:
        conn.close()
        return False

    print("[SEED] Database is empty, populating with seed data...")

    for name, position, email in SEED_MANAGERS:
        conn.execute(
            "INSERT INTO managers (name, position, email) VALUES (?, ?, ?)",
            (name, position, email)
        )
    conn.commit()

    p = SEED_PERIOD
    conn.execute(
        "INSERT INTO periods (name, description, start_date, end_date, is_active) VALUES (?, ?, ?, ?, 1)",
        (p["name"], p["description"], p["start_date"], p["end_date"])
    )
    conn.commit()

    period_id = conn.execute("SELECT id FROM periods ORDER BY id DESC LIMIT 1").fetchone()
    pid = period_id['id'] if isinstance(period_id, dict) else period_id[0]

    managers = conn.execute("SELECT id, name FROM managers WHERE is_active=1").fetchall()
    manager_map = {}
    for m in managers:
        mid = m['id'] if isinstance(m, dict) else m[0]
        mname = m['name'] if isinstance(m, dict) else m[1]
        manager_map[mname] = mid

    for name, token in SEED_TOKENS.items():
        if name not in manager_map:
            continue
        evaluator_id = manager_map[name]
        conn.execute(
            "INSERT INTO tokens (period_id, evaluator_id, token) VALUES (?, ?, ?)",
            (pid, evaluator_id, token)
        )
    conn.commit()

    for name, token in SEED_TOKENS.items():
        if name not in manager_map:
            continue
        evaluator_id = manager_map[name]
        token_row = conn.execute(
            "SELECT id FROM tokens WHERE period_id=? AND evaluator_id=?",
            (pid, evaluator_id)
        ).fetchone()
        token_id = token_row['id'] if isinstance(token_row, dict) else token_row[0]

        for other_name, other_id in manager_map.items():
            if other_id != evaluator_id:
                conn.execute(
                    "INSERT INTO evaluations (token_id, evaluatee_id) VALUES (?, ?)",
                    (token_id, other_id)
                )
    conn.commit()
    conn.close()

    print(f"[SEED] Added {len(SEED_MANAGERS)} managers, 1 period, {len(SEED_TOKENS)} tokens")
    return True
