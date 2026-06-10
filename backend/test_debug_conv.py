import requests
BASE = 'http://127.0.0.1:5000/api'
s = requests.Session()

# Login as new bob2
r = s.post(f'{BASE}/auth/login', json={'email':'bob2@test.ifri.edu','password':'password123'})
if r.status_code != 200:
    print(f'Login failed: {r.status_code} {r.text[:200]}')
    exit()
token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}
uid = r.json()['user']['id']
print(f'Logged in as bob2, uid={uid}')

# Check conversations
r2 = s.get(f'{BASE}/conversations', headers=headers)
print(f'Conversations status: {r2.status_code}')
if r2.status_code == 200:
    data = r2.json()
    convs = data if isinstance(data, list) else data.get('conversations', data.get('data', []))
    print(f'  Count: {len(convs)}')
    for c in convs:
        a = c.get('avec', {})
        print(f'  Conv {c.get("conversation_id")}: avec={a.get("prenom")} {a.get("nom")} avatar_url={a.get("avatar_url")!r}')
        conv_id = c.get('conversation_id')
        if conv_id:
            r3 = s.get(f'{BASE}/conversations/{conv_id}/messages', headers=headers)
            if r3.status_code == 200:
                msgs = r3.json().get('messages', [])
                print(f'    Messages: {len(msgs)}')
                for m in msgs[:2]:
                    snd = m.get('sender', {})
                    print(f'    -> sender={snd.get("prenom")} {snd.get("nom")} avatar={snd.get("avatar_url")!r} txt={m["contenu"][:30]}')

# Check profile/me for email_verified
r4 = s.get(f'{BASE}/profile/me', headers=headers)
print(f'\nProfile/me status: {r4.status_code}')
if r4.status_code == 200:
    p = r4.json()
    print(f'email_verified: {p.get("email_verified")}')
    print(f'has avatar_url: {"avatar_url" in p}')
