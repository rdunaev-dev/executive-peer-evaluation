import requests

BASE = "https://web-production-d9b14.up.railway.app"
r = requests.get(f"{BASE}/evaluate/6214a498-a0d4-4798-a46e-8747b0dda3af/person/10")
print("Status:", r.status_code)

if "score_D1" in r.text:
    print("DEPLOYED: NEW version (12 questions, 5-point scale)")
elif "score_D" in r.text:
    print("DEPLOYED: OLD version (4 questions, 3-point scale)")
else:
    print("UNKNOWN version")

if "16" in r.text and "20" in r.text:
    print("Scale: NEW (4-20)")
if "4-6" in r.text or "7-9" in r.text:
    print("Scale: OLD (4-12)")
