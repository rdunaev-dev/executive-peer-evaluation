"""Update all managers with emails from the employee directory and fix Куприянов."""
from models import get_db, init_db

init_db()
conn = get_db()

updates = {
    "Василий Мехонцев": {"email": "vasilii.m@brl.ru"},
    "Павел Сидогов": {"email": "pavel.sidogov@brl.ru"},
    "Николай Крицюк": {"email": "n.kritsiuk@brl.ru"},
    "Олег Панасюк": {"email": "oleg.mr@brl.ru"},
    "Михаил Ракутько": {"email": "m.rakutko@brl.ru"},
    "Антон Андрюшин": {"email": "a.andryushin@rantsports.com"},
    "Дмитрий Панферов": {"email": "d.panferov@brl.ru"},
    "Артём Паршин": {"email": "a.parshin@brl.ru"},
    "Роман Дунаев": {"email": "r.dunaev@brl.ru"},
    "Мария Вилистер": {"email": "m.wilister@brl.ru"},
}

for name, data in updates.items():
    conn.execute(
        "UPDATE managers SET email=? WHERE name=?",
        (data["email"], name)
    )
    print(f"  Updated email: {name} -> {data['email']}")

conn.execute(
    "UPDATE managers SET name=?, position=? WHERE name=?",
    ("Евгений Куприянов", "Консультант по организационной зрелости", "Куприянова")
)
print("  Fixed: Куприянова -> Евгений Куприянов, Консультант по организационной зрелости")

conn.commit()

rows = conn.execute("SELECT id, name, position, email FROM managers WHERE is_active=1 ORDER BY name").fetchall()
print(f"\n{'='*80}")
print(f"{'#':>3} | {'Имя':<30} | {'Должность':<45} | {'Email'}")
print(f"{'='*80}")
for r in rows:
    print(f"{r['id']:>3} | {r['name']:<30} | {r['position']:<45} | {r['email'] or '—'}")
print(f"{'='*80}")
print(f"Total: {len(rows)} managers")

conn.close()
