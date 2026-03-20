#!/usr/bin/env python3
"""Testa qual é o campo de Flag no Jira"""

import os
import json
import base64
import requests

JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_TOKEN = os.getenv('JIRA_TOKEN')
JIRA_BASE_URL = 'https://picpay.atlassian.net'

def get_jira_auth():
    credentials = f"{JIRA_EMAIL}:{JIRA_TOKEN}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {'Authorization': f'Basic {encoded}'}

# Buscar a issue HCM-788 que sabemos que tem flag
url = f"{JIRA_BASE_URL}/rest/api/2/issue/HCM-788"
headers = get_jira_auth()

response = requests.get(url, headers=headers)
data = response.json()

print("🔍 Todos os campos da issue HCM-788:")
print(json.dumps(list(data['fields'].keys()), indent=2))

print("\n🔍 Campos que contêm 'flag' no nome:")
flag_fields = {k: v for k, v in data['fields'].items() if 'flag' in k.lower()}
print(json.dumps(flag_fields, indent=2, default=str))

print("\n🔍 Campos customizados (customfield_*):")
custom_fields = {k: v for k, v in data['fields'].items() if k.startswith('customfield_')}
for k, v in custom_fields.items():
    if v is not None and v != '' and v != []:
        print(f"  {k}: {v}")
