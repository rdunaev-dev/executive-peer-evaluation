"""Create evaluation period and generate tokens."""
from models import init_db, add_period, get_periods, activate_period, get_tokens_for_period, get_managers

init_db()

period_name = "Q3-Q4 2025 (июль — декабрь 2025)"
period_desc = "Перекрёстная оценка руководителей за последние 6 месяцев. Шкала 1-3 по 4 факторам: Delivery, Ownership, Cross-functional Impact, People & System Leadership."

add_period(period_name, period_desc, "2025-07-01", "2025-12-31")
print(f"Period created: {period_name}")

periods = get_periods()
period = periods[0]
print(f"Period ID: {period['id']}")

activate_period(period['id'])
print("Period activated, tokens generated.\n")

tokens = get_tokens_for_period(period['id'])
managers = {m['id']: m for m in get_managers()}

print(f"{'='*90}")
print(f"{'Руководитель':<35} {'Email':<35} {'Ссылка (токен)'}")
print(f"{'='*90}")

for t in tokens:
    mgr_id = t['evaluator_id']
    mgr = managers.get(mgr_id)
    email = mgr['email'] if mgr else '—'
    link = f"http://127.0.0.1:5000/evaluate/{t['token']}"
    print(f"{t['evaluator_name']:<35} {email:<35} {link}")

print(f"{'='*90}")
print(f"\nTotal: {len(tokens)} evaluation links generated.")
