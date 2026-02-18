"""Update all manager emails to @rantsports.com domain."""
from models import get_db, init_db

init_db()
conn = get_db()

email_map = {
    "Василий Мехонцев": "vasilii.m@rantsports.com",
    "Павел Сидогов": "pavel.sidogov@rantsports.com",
    "Николай Крицюк": "n.kritsiuk@rantsports.com",
    "Олег Панасюк": "oleg.mr@rantsports.com",
    "Михаил Ракутько": "m.rakutko@rantsports.com",
    "Антон Андрюшин": "a.andryushin@rantsports.com",
    "Дмитрий Панферов": "d.panferov@rantsports.com",
    "Артём Паршин": "a.parshin@rantsports.com",
    "Роман Дунаев": "r.dunaev@rantsports.com",
    "Мария Вилистер": "m.wilister@rantsports.com",
    "Евгений Куприянов": "e.kupriyanov@rantsports.com",
}

for name, email in email_map.items():
    conn.execute("UPDATE managers SET email=? WHERE name=?", (email, name))
    print(f"  {name:<30} -> {email}")

conn.commit()

rows = conn.execute("SELECT name, position, email FROM managers WHERE is_active=1 ORDER BY name").fetchall()
print(f"\nAll {len(rows)} managers updated.")

conn.close()
