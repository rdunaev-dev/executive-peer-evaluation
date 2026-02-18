"""Fix manager emails based on Google Workspace directory names."""
from models import get_db, init_db

init_db()
conn = get_db()

email_map = {
    "Василий Мехонцев": "v.mekhontsev@rantsports.com",
    "Павел Сидогов": "p.sidogov@rantsports.com",
    "Николай Крицюк": "n.kritsiuk@rantsports.com",
    "Олег Панасюк": "o.panasyuk@rantsports.com",
    "Михаил Ракутько": "m.rakutko@rantsports.com",
    "Антон Андрюшин": "a.andryushin@rantsports.com",
    "Дмитрий Панферов": "d.panferov@rantsports.com",
    "Артём Паршин": "a.parshin@rantsports.com",
    "Роман Дунаев": "r.dunaev@rantsports.com",
    "Мария Вилистер": "m.vilister@rantsports.com",
    "Евгений Куприянов": "e.kupriyanov@rantsports.com",
}

for name, email in email_map.items():
    conn.execute("UPDATE managers SET email=? WHERE name=?", (email, name))
    print(f"  {name:<30} -> {email}")

conn.commit()
conn.close()
print("\nDone.")
