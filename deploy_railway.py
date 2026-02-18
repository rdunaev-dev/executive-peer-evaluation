"""Deploy to Railway via GraphQL API."""
import json
import urllib.request

TOKEN = "87b01d58-90ba-4313-8c37-182ed8104b95"
API = "https://backboard.railway.com/graphql/v2"
PROJECT_ID = "8d458966-0f20-46ed-afc9-59704845cd8e"
ENV_ID = "2bea30e0-0898-46a0-83e1-29192562997d"
SERVICE_ID = "a3825f05-6368-412a-9420-f6eee9254841"

def gql(query):
    data = json.dumps({"query": query}).encode()
    req = urllib.request.Request(API, data=data, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}")
        return None

# Check current deployments
print("Checking deployments...")
r = gql(f'''
{{
  deployments(
    input: {{
      projectId: "{PROJECT_ID}",
      serviceId: "{SERVICE_ID}",
      environmentId: "{ENV_ID}"
    }}
    first: 3
  ) {{
    edges {{
      node {{
        id
        status
        createdAt
      }}
    }}
  }}
}}
''')
if r:
    print(json.dumps(r, indent=2))

# Trigger a new deploy
print("\nTriggering deploy from GitHub repo...")
r = gql(f'''
mutation {{
  serviceInstanceDeploy(
    serviceId: "{SERVICE_ID}",
    environmentId: "{ENV_ID}"
  )
}}
''')
if r:
    print(json.dumps(r, indent=2))

print("\nApp URL: https://web-production-b0684.up.railway.app")
