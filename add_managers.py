"""Add all managers from the grading spreadsheets."""
from models import init_db, add_manager

init_db()

managers = [
    ("Василий Мехонцев", "Head of Monetisation"),
    ("Павел Сидогов", "Head of SEO"),
    ("Николай Крицюк", "Head of Tech"),
    ("Олег Панасюк", "Head of Media / Главный редактор"),
    ("Михаил Ракутько", "Head of Analytics"),
    ("Антон Андрюшин", "Head of Winscore / Product Lead"),
    ("Дмитрий Панферов", "Head of Engagement"),
    ("Артём Паршин", "Head of Project Office (PMO)"),
    ("Роман Дунаев", "Head of HR"),
    ("Мария Вилистер", "Head of Back Office"),
    ("Куприянова", ""),
]

for name, position in managers:
    add_manager(name, position)
    print(f"+ {name} — {position}")

print(f"\nAll {len(managers)} managers added.")
