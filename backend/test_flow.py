import requests, json

BASE = 'http://127.0.0.1:5000/api'
s = requests.Session()

# 1. Login as Bob
r = s.post(f'{BASE}/auth/login', json={'email':'bob@test.ifri.edu','password':'password123'})
print(f'1. Login: {r.status_code}')
if r.status_code != 200:
    print(f'   Response: {r.text[:200]}')
    exit()
token = r.json().get('token','')
print(f'   Token: OK ({token[:20]}...)')

headers = {'Authorization': f'Bearer {token}'}

# 2. Get Bob's demands
r2 = s.get(f'{BASE}/demands/mine', headers=headers)
print(f'2. Get demands: {r2.status_code}')
if r2.status_code != 200:
    print(f'   Response: {r2.text[:200]}')
else:
    data = r2.json()
    demands = data.get('demands', [])
    print(f'   Demands count: {len(demands)}')
    for d in demands:
        print(f'   - id={d["id"]} matiere={d.get("matiere_nom")} jour={d.get("jour")} creneau={d.get("creneau")}')
    if demands:
        latest = max(demands, key=lambda d: d.get('created_at', ''))
        demand_id = latest['id']
        print(f'   Latest demand_id: {demand_id}')
        
        # 3. Get matching suggestions with latest demand_id
        r3 = s.get(f'{BASE}/matches/suggestions?demand_id={demand_id}', headers=headers)
        print(f'3. Suggestions with demand_id={demand_id}: {r3.status_code}')
        if r3.status_code == 200:
            sug = r3.json()
            matches = sug.get('matches', [])
            print(f'   Matches: {len(matches)}')
            for m in matches:
                print(f'   -> {m["prenom"]} {m["nom"]} score={m["score"]}')
            if not matches:
                print(f'   Message: {sug.get("message","")}')
        else:
            print(f'   Response: {r3.text[:300]}')

# 4. Also test without demand_id
r4 = s.get(f'{BASE}/matches/suggestions', headers=headers)
print(f'4. Suggestions without demand_id: {r4.status_code}')
if r4.status_code == 200:
    sug4 = r4.json()
    matches4 = sug4.get('matches', [])
    print(f'   Matches: {len(matches4)}')
    for m in matches4[:3]:
        print(f'   -> {m["prenom"]} {m["nom"]} score={m["score"]}')
else:
    print(f'   Response: {r4.text[:200]}')
