import requests, re

r = requests.get("https://web-production-d9b14.up.railway.app/evaluate/6214a498-a0d4-4798-a46e-8747b0dda3af")

links = re.findall(r'href="(/evaluate/[^"]*)"', r.text)
print("Evaluate links found:", len(links))
for link in links[:15]:
    print(" ", link)

all_hrefs = re.findall(r'href="([^"]+)"', r.text)
print("\nAll hrefs:")
for h in all_hrefs:
    if 'evaluate' in h:
        print(" ", h)
