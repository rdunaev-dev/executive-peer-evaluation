import sqlite3, os, json

db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evaluation.db')
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

managers = [dict(r) for r in conn.execute('SELECT name, position, email FROM managers WHERE is_active=1 ORDER BY name').fetchall()]
print('MANAGERS = [')
for m in managers:
    print(f'    ("{m["name"]}", "{m["position"]}", "{m["email"]}"),')
print(']')

periods = [dict(r) for r in conn.execute('SELECT name, description, start_date, end_date FROM periods ORDER BY id DESC LIMIT 1').fetchall()]
p = periods[0]
print(f'\nPERIOD = ("{p["name"]}", "{p["description"]}", "{p["start_date"]}", "{p["end_date"]}")')

tokens = conn.execute('''
    SELECT m.name, t.token FROM tokens t
    JOIN managers m ON t.evaluator_id = m.id
    WHERE t.period_id = (SELECT MAX(id) FROM periods)
    ORDER BY m.name
''').fetchall()
print('\nTOKENS = {')
for t in tokens:
    print(f'    "{t[0]}": "{t[1]}",')
print('}')

conn.close()
