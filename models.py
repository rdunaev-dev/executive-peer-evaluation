"""
Database models and operations for the Executive Peer Evaluation System.
Supports SQLite (local) and PostgreSQL (production via DATABASE_URL).
"""

import sqlite3
import uuid
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evaluation.db')

DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras


class DBConnection:
    """Unified wrapper for SQLite and PostgreSQL connections."""

    def __init__(self):
        if USE_POSTGRES:
            self._conn = psycopg2.connect(DATABASE_URL)
        else:
            self._conn = sqlite3.connect(DB_PATH)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")

    def execute(self, sql, params=None):
        if USE_POSTGRES:
            sql = sql.replace('?', '%s')
            cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql, params or ())
            return cur
        else:
            return self._conn.execute(sql, params) if params else self._conn.execute(sql)

    def executescript(self, sql):
        if USE_POSTGRES:
            cur = self._conn.cursor()
            cur.execute(sql)
            return cur
        else:
            return self._conn.executescript(sql)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

# ─────────────────────────────────────────────
# Questions definition (methodology)
# Based on the Head grading system (A/B/C)
# PersonScore = D + O + X + L (range 4-12)
# Head C = 4-6, Head B = 7-9, Head A = 10-12
# ─────────────────────────────────────────────

MAX_SCORE = 4
NUM_CRITERIA = 4

BLOCKS = [
    {
        "id": "delivery",
        "code": "D",
        "name": "Delivery & Performance",
        "name_ru": "Результаты",
        "icon": "📊",
        "description": "Оцените надёжность и качество результатов этого руководителя.",
        "sub_criteria": [
            "Насколько вы можете положиться на сроки и качество его работы, когда его результаты влияют на ваши задачи?",
            "Как он справляется с серьёзными препятствиями — находит решения сам или эскалирует и ждёт?",
            "Насколько стабильны его результаты от периода к периоду — есть системность или всё зависит от ситуации?",
        ],
        "questions": [
            {
                "code": "D",
                "text": "Delivery & Performance — Результаты",
                "hint": "Подумайте о надёжности результатов, способности преодолевать препятствия и стабильности работы этого руководителя.",
            },
        ]
    },
    {
        "id": "ownership",
        "code": "O",
        "name": "Ownership & Proactivity",
        "name_ru": "Владение и проактивность",
        "icon": "🚀",
        "description": "Оцените проактивность и ответственность этого руководителя.",
        "sub_criteria": [
            "Как часто он инициирует изменения и улучшения — не дожидаясь запроса сверху или от коллег?",
            "Когда в его зоне возникает проблема — как быстро берёт ответственность на себя, а не перекладывает?",
            "Способен ли он предвидеть риски и действовать на опережение — или скорее тушит пожары по факту?",
        ],
        "questions": [
            {
                "code": "O",
                "text": "Ownership & Proactivity — Владение и проактивность",
                "hint": "Подумайте об инициативности, скорости принятия ответственности и способности работать на опережение.",
            },
        ]
    },
    {
        "id": "crossfunc",
        "code": "X",
        "name": "Cross-functional Impact",
        "name_ru": "Влияние за границами роли",
        "icon": "🔗",
        "description": "Оцените влияние этого руководителя за пределами своей функции.",
        "sub_criteria": [
            "Когда вам нужна была помощь или экспертиза — насколько быстро и конструктивно он включался?",
            "Учитывает ли он влияние своих решений на другие команды и бизнес в целом?",
            "В совместных проектах — делает минимум по своей части или реально выходит за рамки и усиливает общий результат?",
        ],
        "questions": [
            {
                "code": "X",
                "text": "Cross-functional Impact — Влияние за границами роли",
                "hint": "Подумайте об отзывчивости, системном мышлении и вкладе в кросс-функциональные проекты.",
            },
        ]
    },
    {
        "id": "leadership",
        "code": "L",
        "name": "People & System Leadership",
        "name_ru": "Люди и системы",
        "icon": "👥",
        "description": "Оцените, как этот руководитель строит команду и системы.",
        "sub_criteria": [
            "Может ли его команда работать эффективно в его отсутствие — или всё замыкается на нём лично?",
            "Насколько устойчивы и масштабируемы процессы и системы, которые он построил?",
            "Растут ли люди в его команде — видите ли вы развитие их компетенций и карьеры?",
        ],
        "questions": [
            {
                "code": "L",
                "text": "People & System Leadership — Люди и системы",
                "hint": "Подумайте об автономности команды, устойчивости процессов и развитии людей.",
            },
        ]
    },
]

ALL_QUESTIONS = []
for block in BLOCKS:
    for q in block["questions"]:
        ALL_QUESTIONS.append(q)

SCORE_LABELS = {
    1: "Не соответствует ожиданиям",
    2: "Частично соответствует",
    3: "Полностью соответствует",
    4: "Превосходит ожидания",
}

NA_SCORE = 0
NA_LABEL = "Н/И — недостаточно информации"

MAX_PERSON_SCORE = NUM_CRITERIA * MAX_SCORE  # 16


def get_db():
    """Get database connection."""
    return DBConnection()


SCHEMA_SQLITE = """
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
"""

SCHEMA_POSTGRES = """
    CREATE TABLE IF NOT EXISTS managers (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        position TEXT NOT NULL,
        email TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS periods (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        is_active INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS tokens (
        id SERIAL PRIMARY KEY,
        period_id INTEGER NOT NULL REFERENCES periods(id),
        evaluator_id INTEGER NOT NULL REFERENCES managers(id),
        token TEXT NOT NULL UNIQUE,
        is_completed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS evaluations (
        id SERIAL PRIMARY KEY,
        token_id INTEGER NOT NULL REFERENCES tokens(id),
        evaluatee_id INTEGER NOT NULL REFERENCES managers(id),
        is_completed INTEGER DEFAULT 0,
        advice TEXT,
        completed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS responses (
        id SERIAL PRIMARY KEY,
        evaluation_id INTEGER NOT NULL REFERENCES evaluations(id),
        question_code TEXT NOT NULL,
        score INTEGER,
        justification TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""


def init_db():
    """Initialize database tables."""
    conn = get_db()
    conn.executescript(SCHEMA_POSTGRES if USE_POSTGRES else SCHEMA_SQLITE)
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
    question_data = defaultdict(lambda: {"scores": [], "justifications": [], "na_count": 0})

    for r in responses:
        if r['score'] is not None and r['score'] > 0:
            question_data[r['question_code']]["scores"].append(r['score'])
        elif r['score'] == 0:
            question_data[r['question_code']]["na_count"] += 1
        if r['justification'] and r['justification'].strip():
            question_data[r['question_code']]["justifications"].append(r['justification'])

    # Calculate aggregated results (Н/И scores excluded from averages)
    results = {}
    for code, data in question_data.items():
        scores = data['scores']
        avg = round(sum(scores) / len(scores), 2) if scores else 0
        results[code] = {
            "avg_score": avg,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "count": len(scores),
            "na_count": data['na_count'],
            "justifications": data['justifications']
        }

    # With 4 blocks × 1 question each, results already keyed by block code (D, O, X, L)
    criterion_avgs = {}
    for block in BLOCKS:
        code = block["code"]
        criterion_avgs[code] = results[code]["avg_score"] if code in results else 0

    total_avg = sum(criterion_avgs.values())
    total_avg_rounded = round(total_avg, 1)

    # Collect advice
    advices = [e['advice'] for e in evaluations if e['advice'] and e['advice'].strip()]

    # Get manager info
    manager = conn.execute("SELECT * FROM managers WHERE id=?", (manager_id,)).fetchone()

    conn.close()

    return {
        "manager": dict(manager),
        "evaluator_count": len(evaluations),
        "questions": results,
        "criterion_avgs": criterion_avgs,
        "advices": advices,
        "person_score": total_avg_rounded,
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
