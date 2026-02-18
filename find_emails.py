"""Find manager emails from the employee list files."""
import json
import glob
import os

agent_dir = r"C:\Users\msi\.cursor\projects\c-Users-msi-cursor-projects-heads\agent-tools"

names_to_find = [
    "Мехонцев", "Сидогов", "Крицюк", "Панасюк", "Ракутько",
    "Андрюшин", "Панферов", "Паршин", "Дунаев", "Вилистер", "Куприянов"
]

found = set()

for fpath in [
    os.path.join(agent_dir, "95b92eb8-4f17-464b-b2bd-2ee598e077e0.txt"),
    os.path.join(agent_dir, "31379110-b13e-4438-837d-fdc09773fb34.txt"),
]:
    if not os.path.exists(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = data.get("values", [])
    for row in rows:
        fio = row[0] if len(row) > 0 else ""
        for name in names_to_find:
            if name in fio and name not in found:
                position = row[2] if len(row) > 2 else ""
                email = row[8] if len(row) > 8 else ""
                email = email.strip()
                print(f"{fio} | {position} | {email}")
                found.add(name)

missing = [n for n in names_to_find if n not in found]
if missing:
    print(f"\nNot found: {', '.join(missing)}")
