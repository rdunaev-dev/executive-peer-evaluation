"""
Database models and operations for the Executive Peer Evaluation System.
Uses SQLite for simplicity and portability.
"""

import sqlite3
import uuid
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evaluation.db')

# ─────────────────────────────────────────────
# Questions definition (methodology)
# ─────────────────────────────────────────────

BLOCKS = [
    {
        "id": "block1",
        "name": "Стратегическое мышление и принятие решений",
        "icon": "🧠",
        "questions": [
            {"code": "1.1", "text": "Принимает решения, учитывая интересы компании в целом, а не только своей функции"},
            {"code": "1.2", "text": "Действует проактивно: предвидит риски и возможности, а не только реагирует на проблемы"},
            {"code": "1.3", "text": "Способен аргументировать свою позицию данными и менять её при появлении новой информации"},
        ]
    },
    {
        "id": "block2",
        "name": "Кросс-функциональное сотрудничество",
        "icon": "🤝",
        "questions": [
            {"code": "2.1", "text": "Активно инициирует взаимодействие с коллегами для решения общих задач"},
            {"code": "2.2", "text": "Готов идти на компромисс и жертвовать интересами своей функции ради общей цели"},
            {"code": "2.3", "text": "Выполняет договорённости, достигнутые на уровне топ-команды, в полном объёме и в срок"},
        ]
    },
    {
        "id": "block3",
        "name": "Лидерство и влияние",
        "icon": "🌟",
        "questions": [
            {"code": "3.1", "text": "Вдохновляет и мотивирует людей вокруг себя (не только свою команду)"},
            {"code": "3.2", "text": "Создаёт устойчивые процессы и системы, а не замыкает всё на себе"},
            {"code": "3.3", "text": "Открыт к обратной связи и демонстрирует готовность меняться"},
        ]
    },
    {
        "id": "block4",
        "name": "Управление в условиях давления",
        "icon": "💪",
        "questions": [
            {"code": "4.1", "text": "Сохраняет конструктивность и ясность коммуникации в стрессовых ситуациях"},
            {"code": "4.2", "text": "Берёт на себя ответственность за ошибки, а не перекладывает на других"},
            {"code": "4.3", "text": "Поддерживает коллег в сложных ситуациях, а не дистанцируется"},
        ]
    },
    {
        "id": "block5",
        "name": "Вклад в команду топ-менеджеров",
        "icon": "👥",
        "questions": [
            {"code": "5.1", "text": "Привносит ценность в дискуссии топ-команды (а не отсиживается или доминирует)"},
            {"code": "5.2", "text": "Поддерживает решения, принятые командой, даже если изначально был против"},
            {"code": "5.3", "text": "Делится информацией и ресурсами проактивно, без необходимости просить"},
        ]
    },
]

ALL_QUESTIONS = []
for block in BLOCKS:
    for q in block["questions"]:
        ALL_QUESTIONS.append(q)

SCORE_LABELS = {
    5: "Превосходно — является примером, проявляется стабильно",
    4: "Хорошо — проявляется в большинстве ситуаций",
    3: "Достаточно — проявляется ситуативно, есть зона для улучшения",
    2: "Требует улучшения — проявляется редко, создаёт проблемы",
    1: "Критично — не проявляется или проявляется противоположное",
}


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            email TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            is_active INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period_id INTEGER NOT NULL,
            evaluator_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            is_completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (period_id) REFERENCES periods(id),
            FOREIGN KEY (evaluator_id) REFERENCES managers(id)
        );

        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id INTEGER NOT NULL,
            evaluatee_id INTEGER NOT NULL,
            is_completed INTEGER DEFAULT 0,
            advice TEXT,
            completed_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (token_id) REFERENCES tokens(id),
            FOREIGN KEY (evaluatee_id) REFERENCES managers(id)
        );

        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id INTEGER NOT NULL,
            question_code TEXT NOT NULL,
            score INTEGER,
            justification TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
        );
    """)
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# Manager operations
# ─────────────────────────────────────────────

def add_manager(name, position, email=""):
    conn = get_db()
    conn.execute(
        "INSERT INTO managers (name, position, email) VALUES (?, ?, ?)",
        (name, position, email)
    )
    conn.commit()
    conn.close()


def get_managers(active_only=True):
    conn = get_db()
    if active_only:
        rows = conn.execute("SELECT * FROM managers WHERE is_active=1 ORDER BY name").fetchall()
    else:
        rows = conn.execute("SELECT * FROM managers ORDER BY name").fetchall()
    conn.close()
    return rows


def get_manager(manager_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM managers WHERE id=?", (manager_id,)).fetchone()
    conn.close()
    return row


def update_manager(manager_id, name, position, email=""):
    conn = get_db()
    conn.execute(
        "UPDATE managers SET name=?, position=?, email=? WHERE id=?",
        (name, position, email, manager_id)
    )
    conn.commit()
    conn.close()


def delete_manager(manager_id):
    conn = get_db()
    conn.execute("UPDATE managers SET is_active=0 WHERE id=?", (manager_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# Period operations
# ─────────────────────────────────────────────

def add_period(name, description, start_date, end_date):
    conn = get_db()
    conn.execute(
        "INSERT INTO periods (name, description, start_date, end_date) VALUES (?, ?, ?, ?)",
        (name, description, start_date, end_date)
    )
    conn.commit()
    conn.close()


def get_periods():
    conn = get_db()
    rows = conn.execute("SELECT * FROM periods ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows


def get_period(period_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM periods WHERE id=?", (period_id,)).fetchone()
    conn.close()
    return row


def activate_period(period_id):
    """Activate a period and generate tokens for all manager pairs."""
    conn = get_db()

    # Deactivate all other periods
    conn.execute("UPDATE periods SET is_active=0")

    # Activate this one
    conn.execute("UPDATE periods SET is_active=1 WHERE id=?", (period_id,))

    # Check if tokens already exist
    existing = conn.execute(
        "SELECT COUNT(*) as cnt FROM tokens WHERE period_id=?", (period_id,)
    ).fetchone()['cnt']

    if existing == 0:
        # Generate tokens for each evaluator
        managers = conn.execute("SELECT id FROM managers WHERE is_active=1").fetchall()
        for evaluator in managers:
            token = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO tokens (period_id, evaluator_id, token) VALUES (?, ?, ?)",
                (period_id, evaluator['id'], token)
            )

            # Create evaluation entries for each evaluatee (excluding self)
            for evaluatee in managers:
                if evaluatee['id'] != evaluator['id']:
                    token_id = conn.execute(
                        "SELECT id FROM tokens WHERE period_id=? AND evaluator_id=?",
                        (period_id, evaluator['id'])
                    ).fetchone()['id']
                    conn.execute(
                        "INSERT INTO evaluations (token_id, evaluatee_id) VALUES (?, ?)",
                        (token_id, evaluatee['id'])
                    )

    conn.commit()
    conn.close()


def deactivate_period(period_id):
    conn = get_db()
    conn.execute("UPDATE periods SET is_active=0 WHERE id=?", (period_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# Token / Evaluation operations
# ─────────────────────────────────────────────

def get_tokens_for_period(period_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT t.*, m.name as evaluator_name, m.position as evaluator_position,
               (SELECT COUNT(*) FROM evaluations WHERE token_id=t.id AND is_completed=1) as completed_count,
               (SELECT COUNT(*) FROM evaluations WHERE token_id=t.id) as total_count
        FROM tokens t
        JOIN managers m ON t.evaluator_id = m.id
        WHERE t.period_id = ?
        ORDER BY m.name
    """, (period_id,)).fetchall()
    conn.close()
    return rows


def get_token_data(token):
    conn = get_db()
    row = conn.execute("""
        SELECT t.*, p.name as period_name, p.description as period_description,
               p.start_date, p.end_date, p.is_active as period_active,
               m.name as evaluator_name
        FROM tokens t
        JOIN periods p ON t.period_id = p.id
        JOIN managers m ON t.evaluator_id = m.id
        WHERE t.token = ?
    """, (token,)).fetchone()
    conn.close()
    return row


def get_evaluations_for_token(token_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT e.*, m.name as evaluatee_name, m.position as evaluatee_position
        FROM evaluations e
        JOIN managers m ON e.evaluatee_id = m.id
        WHERE e.token_id = ?
        ORDER BY m.name
    """, (token_id,)).fetchall()
    conn.close()
    return rows


def get_evaluation(evaluation_id):
    conn = get_db()
    row = conn.execute("""
        SELECT e.*, m.name as evaluatee_name, m.position as evaluatee_position,
               t.token, t.evaluator_id
        FROM evaluations e
        JOIN managers m ON e.evaluatee_id = m.id
        JOIN tokens t ON e.token_id = t.id
        WHERE e.id = ?
    """, (evaluation_id,)).fetchone()
    conn.close()
    return row


def save_evaluation(evaluation_id, scores_data, advice):
    """
    Save evaluation responses.
    scores_data: list of dicts with {question_code, score, justification}
    """
    conn = get_db()

    # Delete existing responses for this evaluation
    conn.execute("DELETE FROM responses WHERE evaluation_id=?", (evaluation_id,))

    # Insert new responses
    for item in scores_data:
        conn.execute(
            "INSERT INTO responses (evaluation_id, question_code, score, justification) VALUES (?, ?, ?, ?)",
            (evaluation_id, item['question_code'], item['score'], item['justification'])
        )

    # Mark evaluation as completed
    conn.execute(
        "UPDATE evaluations SET is_completed=1, advice=?, completed_at=datetime('now') WHERE id=?",
        (advice, evaluation_id)
    )

    # Check if all evaluations for this token are complete
    token_id = conn.execute(
        "SELECT token_id FROM evaluations WHERE id=?", (evaluation_id,)
    ).fetchone()['token_id']

    incomplete = conn.execute(
        "SELECT COUNT(*) as cnt FROM evaluations WHERE token_id=? AND is_completed=0",
        (token_id,)
    ).fetchone()['cnt']

    if incomplete == 0:
        conn.execute("UPDATE tokens SET is_completed=1 WHERE id=?", (token_id,))

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# Report operations
# ─────────────────────────────────────────────

def get_report_for_manager(period_id, manager_id):
    """Get aggregated anonymous report for a manager in a period."""
    conn = get_db()

    # Get all completed evaluations for this manager
    evaluations = conn.execute("""
        SELECT e.id, e.advice
        FROM evaluations e
        JOIN tokens t ON e.token_id = t.id
        WHERE t.period_id = ? AND e.evaluatee_id = ? AND e.is_completed = 1
    """, (period_id, manager_id)).fetchall()

    if not evaluations:
        conn.close()
        return None

    eval_ids = [e['id'] for e in evaluations]
    placeholders = ','.join('?' * len(eval_ids))

    # Get all responses
    responses = conn.execute(f"""
        SELECT question_code, score, justification
        FROM responses
        WHERE evaluation_id IN ({placeholders})
        ORDER BY question_code
    """, eval_ids).fetchall()

    # Aggregate by question
    from collections import defaultdict
    question_data = defaultdict(lambda: {"scores": [], "justifications": []})

    for r in responses:
        if r['score'] is not None and r['score'] > 0:
            question_data[r['question_code']]["scores"].append(r['score'])
        if r['justification'] and r['justification'].strip():
            question_data[r['question_code']]["justifications"].append(r['justification'])

    # Calculate aggregated results
    results = {}
    for code, data in question_data.items():
        scores = data['scores']
        avg = round(sum(scores) / len(scores) * 2) / 2 if scores else 0  # Round to 0.5
        results[code] = {
            "avg_score": avg,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "count": len(scores),
            "justifications": data['justifications']
        }

    # Collect advice
    advices = [e['advice'] for e in evaluations if e['advice'] and e['advice'].strip()]

    # Get manager info
    manager = conn.execute("SELECT * FROM managers WHERE id=?", (manager_id,)).fetchone()

    conn.close()

    return {
        "manager": dict(manager),
        "evaluator_count": len(evaluations),
        "questions": results,
        "advices": advices
    }


def get_period_completion_stats(period_id):
    """Get completion statistics for a period."""
    conn = get_db()

    total_evaluations = conn.execute("""
        SELECT COUNT(*) as cnt FROM evaluations e
        JOIN tokens t ON e.token_id = t.id
        WHERE t.period_id = ?
    """, (period_id,)).fetchone()['cnt']

    completed_evaluations = conn.execute("""
        SELECT COUNT(*) as cnt FROM evaluations e
        JOIN tokens t ON e.token_id = t.id
        WHERE t.period_id = ? AND e.is_completed = 1
    """, (period_id,)).fetchone()['cnt']

    total_tokens = conn.execute(
        "SELECT COUNT(*) as cnt FROM tokens WHERE period_id=?", (period_id,)
    ).fetchone()['cnt']

    completed_tokens = conn.execute(
        "SELECT COUNT(*) as cnt FROM tokens WHERE period_id=? AND is_completed=1", (period_id,)
    ).fetchone()['cnt']

    conn.close()

    return {
        "total_evaluations": total_evaluations,
        "completed_evaluations": completed_evaluations,
        "total_tokens": total_tokens,
        "completed_tokens": completed_tokens,
        "percent": round(completed_evaluations / total_evaluations * 100) if total_evaluations > 0 else 0
    }
